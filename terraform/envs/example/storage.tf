
resource "google_storage_bucket" "main" {
  name     = "${var.gcp_project_id}-${var.app_name}"
  location = var.gcp_region
}

resource "google_storage_bucket" "dead_letter" {
  name                        = "${var.gcp_project_id}-${var.app_name}-dlq"
  location                    = var.gcp_region
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
}
