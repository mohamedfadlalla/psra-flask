import unittest
from app import app, db
from models import User

class DashboardTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_dashboard_requires_login(self):
        response = self.app.get('/dashboard')
        self.assertEqual(response.status_code, 302) # Redirects to login
