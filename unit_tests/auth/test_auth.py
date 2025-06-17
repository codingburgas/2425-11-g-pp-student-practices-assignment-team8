import unittest
from src.auth.send_verification import generate_verification_code

class TestAuth(unittest.TestCase):
    def test_generate_code_length(self):
        code = generate_verification_code()
        self.assertTrue(100000 <= code <= 999999)