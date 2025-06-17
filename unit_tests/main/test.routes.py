import unittest
from flask import session
from src import create_app
from config import Config

class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app(Config).test_client()
        self.app.testing = True

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_poll_get(self):
        response = self.app.get('/poll')
        self.assertEqual(response.status_code, 200)