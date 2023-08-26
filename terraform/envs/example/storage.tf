
resource "google_storage_bucket" "bucket" {
  name     = "${var.gcp_project_id}-${var.app_name}"
  location = var.gcp_region
}

resource "google_storage_bucket_iam_member" "member" {
  bucket = google_storage_bucket.bucket.name
  role   = "roles/storage.admin"
  member = "serviceAccount:${google_service_account.app.email}"
}
