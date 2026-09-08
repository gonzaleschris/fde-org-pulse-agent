output "cloud_run_service_uri" {
  description = "URI of the deployed Cloud Run agent service"
  value       = google_cloud_run_v2_service.fde_pulse_agent.uri
}

output "service_account_email" {
  description = "Service Account email used by the Agent"
  value       = google_service_account.agent_sa.email
}

output "secret_gemini_key_id" {
  description = "Secret Manager ID for Gemini API Key"
  value       = google_secret_manager_secret.gemini_api_key.id
}
