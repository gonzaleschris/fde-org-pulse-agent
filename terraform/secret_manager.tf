# Google Cloud Secret Manager for Secure API Key Management
resource "google_secret_manager_secret" "gemini_api_key" {
  secret_id = "gemini-api-key"

  replication {
    auto {}
  }

  labels = {
    environment = "production"
    app         = "fde-org-pulse-agent"
  }
}

resource "google_secret_manager_secret" "chat_webhook" {
  secret_id = "google-chat-webhook-url"

  replication {
    auto {}
  }

  labels = {
    environment = "production"
    app         = "fde-org-pulse-agent"
  }
}
