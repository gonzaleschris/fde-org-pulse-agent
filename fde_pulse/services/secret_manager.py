"""Google Cloud Secret Manager client with environment fallback."""
import os
import logging
from typing import Optional

logger = logging.getLogger("fde_pulse.secrets")

class SecretManagerService:
    """Manages secure retrieval of API keys and credentials from Google Cloud Secret Manager."""

    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID", "fde-ai-agent-platform")
        self._client = None
        self._initialized = False

    def _get_client(self):
        if not self._initialized:
            try:
                from google.cloud import secretmanager
                self._client = secretmanager.SecretManagerServiceClient()
            except ImportError:
                logger.info("google-cloud-secret-manager not installed. Using local environment secrets.")
                self._client = None
            except Exception as e:
                logger.warning(f"Could not initialize SecretManagerServiceClient: {e}. Falling back to env.")
                self._client = None
            self._initialized = True
        return self._client

    def get_secret(self, secret_id: str, version_id: str = "latest") -> Optional[str]:
        """Fetches a secret from GCP Secret Manager, falling back to OS environment variables.
        
        Args:
            secret_id: Name of the secret in GCP Secret Manager or env variable name.
            version_id: Version string (defaults to 'latest').

        Returns:
            The secret string, or None if unavailable.
        """
        # 1. First check environment variables
        env_val = os.getenv(secret_id.upper().replace("-", "_")) or os.getenv(secret_id)
        if env_val:
            return env_val

        # 2. Try Google Cloud Secret Manager
        client = self._get_client()
        if client and self.project_id:
            try:
                name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version_id}"
                response = client.access_secret_version(request={"name": name})
                return response.payload.data.decode("UTF-8").strip()
            except Exception as e:
                logger.warning(f"Failed to access secret '{secret_id}' from GCP Secret Manager: {e}")

        return None
