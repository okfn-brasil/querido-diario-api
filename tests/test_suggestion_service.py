from unittest import TestCase
from unittest.mock import MagicMock

from suggestions import (
    Suggestion,
    SuggestionServiceInterface,
    MailjetSuggestionService,
    create_suggestion_service,
)


class MailjetSuggestionServiceTest(TestCase):
    def setUp(self):
        self.mailjet_client = MagicMock()

        self.subject = MailjetSuggestionService(
            mailjet_client=self.mailjet_client,
            suggestion_sender_name="Sender Name",
            suggestion_sender_email="sender-email@address",
            suggestion_recipient_name="Recipient Name",
            suggestion_recipient_email="recipient-email@address",
            suggestion_mailjet_custom_id="custom_id",
        )

    def test_send_email(self):
        data = {
            "Messages": [
                {
                    "From": {"Name": "Sender Name", "Email": "sender-email@address",},
                    "To": [
                        {"Name": "Recipient Name", "Email": "recipient-email@address",}
                    ],
                    "Subject": "Querido Diário, hoje recebi uma sugestão",
                    "TextPart": f"From My Name <email@address.com>:\n\nContent of suggestion",
                    "CustomID": "custom_id",
                }
            ]
        }
        self.mailjet_client.send.create(data=data).configure_mock(status_code=200)

        suggestion_result = self.subject.add_suggestion(
            Suggestion(
                email_address="email@address.com",
                name="My Name",
                content="Content of suggestion",
            )
        )

        self.assertTrue(suggestion_result)
        self.mailjet_client.send.create.assert_called_with(data=data)

    def test_not_send_email(self):
        data = {
            "Messages": [
                {
                    "From": {"Name": "Sender Name", "Email": "sender-email@address",},
                    "To": [
                        {"Name": "Recipient Name", "Email": "recipient-email@address",}
                    ],
                    "Subject": "Querido Diário, hoje recebi uma sugestão",
                    "TextPart": f"From A girl has no name <wrong@address.com>:\n\nArgument Clinic",
                    "CustomID": "custom_id",
                }
            ]
        }
        self.mailjet_client.send.create(data=data).configure_mock(status_code=401)

        suggestion_result = self.subject.add_suggestion(
            Suggestion(
                email_address="wrong@address.com",
                name="A girl has no name",
                content="Argument Clinic",
            )
        )

        self.assertFalse(suggestion_result)
        self.mailjet_client.send.create.assert_called_with(data=data)


class SuggestionServiceFactory(TestCase):
    def test_create_suggestion_service(self):
        suggestion_service = create_suggestion_service(
            suggestion_mailjet_rest_api_key="suggestion_mailjet_rest_api_key",
            suggestion_mailjet_rest_api_secret="suggestion_mailjet_rest_api_secret",
            suggestion_sender_name="suggestion_sender_name",
            suggestion_sender_email="suggestion_sender_email",
            suggestion_recipient_name="suggestion_recipient_name",
            suggestion_recipient_email="suggestion_recipient_email",
            suggestion_mailjet_custom_id="suggestion_mailjet_custom_id",
        )
        self.assertIsInstance(suggestion_service, SuggestionServiceInterface)
