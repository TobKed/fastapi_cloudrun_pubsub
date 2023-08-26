resource "google_artifact_registry_repository" "repository" {
  description   = "Docker repository for ${var.app_name}"
  format        = "DOCKER"
  location      = var.gcp_region
  project       = var.gcp_project_id
  repository_id = "${var.app_name}-repository"

  depends_on = [module.enable_google_apis]
}
