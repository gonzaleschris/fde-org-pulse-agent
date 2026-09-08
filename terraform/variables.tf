variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
  default     = "fde-ai-agent-platform"
}

variable "region" {
  description = "Google Cloud Region"
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Name of the FDE Org Pulse Agent Cloud Run Service"
  type        = string
  default     = "fde-org-pulse-agent"
}

variable "image_tag" {
  description = "Container image tag to deploy"
  type        = string
  default     = "gcr.io/fde-ai-agent-platform/fde-org-pulse-agent:latest"
}
