import unittest
import os
from fde_pulse.services.secret_manager import SecretManagerService

class TestSecretManager(unittest.TestCase):
    def test_env_secret_fallback(self):
        os.environ["GEMINI_API_KEY"] = "test-mock-key-12345"
        svc = SecretManagerService(project_id="test-proj")
        secret = svc.get_secret("GEMINI_API_KEY")
        self.assertEqual(secret, "test-mock-key-12345")

    def test_missing_secret(self):
        svc = SecretManagerService(project_id="test-proj")
        secret = svc.get_secret("NON_EXISTENT_SECRET_XYZ")
        self.assertIsNone(secret)

if __name__ == "__main__":
    unittest.main()
