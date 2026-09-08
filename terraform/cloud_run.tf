# Cloud Run Job / Service for Automated Weekly Agent Execution
resource "google_cloud_run_v2_service" "fde_pulse_agent" {
  name     = var.service_name
  location = var.region
  ingress  = "INGRESS_TRAFFIC_INTERNAL_ONLY"

  template {
    service_account = google_service_account.agent_sa.email

    containers {
      image = var.image_tag

      resources {
        limits = {
          cpu    = "2"
          memory = "2Gi"
        }
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "PYTHONUNBUFFERED"
        value = "1"
      }
    }
  }
}
