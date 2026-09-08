# Dedicated IAM Service Account for FDE Org Pulse Agent
resource "google_service_account" "agent_sa" {
  account_id   = "fde-pulse-agent-sa"
  display_name = "FDE Org Pulse Agent Service Account"
}

# Grant access to Secret Manager
resource "google_secret_manager_secret_iam_member" "secret_accessor" {
  secret_id = google_secret_manager_secret.gemini_api_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.agent_sa.email}"
}

# Grant Vertex AI User role for Gemini 2.0 model execution
resource "google_project_iam_member" "vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.agent_sa.email}"
}
