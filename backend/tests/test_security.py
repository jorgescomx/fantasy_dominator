import sys
from pathlib import Path

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.app.core.config import settings
from backend.app.main import app


class SecurityTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()

    def test_health_is_public(self):
        with patch.object(settings, "API_KEY", ""):
            self.assertEqual(self.client.get("/api/v1/health").status_code, 200)

    def test_api_key_protects_api_and_browser_session_works(self):
        with patch.object(settings, "API_KEY", "test-key"):
            self.assertEqual(self.client.get("/api/v1/draft/state").status_code, 401)
            self.assertEqual(
                self.client.get(
                    "/api/v1/draft/state", headers={"X-API-Key": "test-key"}
                ).status_code,
                200,
            )

            page = self.client.get("/")
            self.assertEqual(page.status_code, 200)
            self.assertIn("fd_session", page.cookies)
            self.assertEqual(self.client.get("/api/v1/draft/state").status_code, 200)

    def test_connect_rejects_invalid_league_id(self):
        with patch.object(settings, "API_KEY", "test-key"):
            response = self.client.post(
                "/api/v1/league/connect",
                headers={"X-API-Key": "test-key"},
                json={"league_id": "not-a-number"},
            )
            self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
