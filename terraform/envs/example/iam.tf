resource "google_service_account" "app" {
  account_id   = "${var.app_name}-sa"
  display_name = "Service Account for ${var.app_name}"
}

resource "google_service_account" "pubsub" {
  account_id   = "pubsub-invoker"
  display_name = "Cloud Run Pub/Sub Invoker"
}
