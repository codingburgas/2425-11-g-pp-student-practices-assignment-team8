import unittest
from src import create_app
from config import Config

class TestProfileRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app(Config).test_client()
        self.app.testing = True

    def test_settings_access(self):
        response = self.app.get('/settings')
        self.assertIn(response.status_code, [200, 302])  # Redirect or OK

    def test_profile_route_exists(self):
        response = self.app.get('/profile')
        self.assertIn(response.status_code, [200, 302])