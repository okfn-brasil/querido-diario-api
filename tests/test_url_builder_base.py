"""
Base test class for URL builder tests to reduce code duplication.
"""

import os
import unittest
from unittest.mock import patch


class BaseUrlBuilderTest(unittest.TestCase):
    """
    Base class for URL builder tests with common setUp/tearDown.
    """

    def setUp(self):
        """Set up environment patcher before each test"""
        self.env_patcher = patch.dict(os.environ, {}, clear=True)
        self.env_patcher.start()

    def tearDown(self):
        """Clean up environment patcher after each test"""
        self.env_patcher.stop()

    def set_env(self, **kwargs):
        """Helper to set environment variables"""
        for key, value in kwargs.items():
            os.environ[key] = value

    def assert_url_equals(self, actual, expected):
        """Helper for asserting URLs with better error messages"""
        self.assertEqual(actual, expected, f"Expected URL: {expected}, Got: {actual}")
