import asyncio
import threading
from unittest import TestCase

import httpx

from api import app, configure_api_app
from tests.test_helpers import create_default_mocks, create_mock_gazette_interface


class BlockingEndpointsTests(TestCase):
    """
    The search engine and database clients are synchronous. If an endpoint that
    calls them is declared with `async def`, a slow query blocks the event loop
    and every other request waits for it, including /health, which makes the
    load balancer take the instance out of rotation.
    """

    def test_health_check_should_answer_while_a_gazette_search_is_running(self):
        search_started = threading.Event()
        health_answered = threading.Event()

        def slow_search(_request):
            search_started.set()
            health_answered.wait(timeout=5)
            return 0, []

        interface = create_mock_gazette_interface()
        interface.get_gazettes.side_effect = slow_search
        configure_api_app(interface, *create_default_mocks()[1:])

        finished = []

        async def request(client, path):
            response = await client.get(path)
            finished.append(path)
            if path == "/health":
                health_answered.set()
            return response

        async def scenario():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                search = asyncio.create_task(request(client, "/gazettes"))
                await asyncio.to_thread(search_started.wait, 5)
                health = await request(client, "/health")
                return await search, health

        search, health = asyncio.run(scenario())

        self.assertEqual(health.status_code, 200)
        self.assertEqual(search.status_code, 200)
        self.assertEqual(["/health", "/gazettes"], finished)
