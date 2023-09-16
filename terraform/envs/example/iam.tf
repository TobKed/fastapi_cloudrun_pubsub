resource "google_service_account" "app" {
  # account id can not be longer than 28 characters
  account_id   = substr("${var.app_name}-sa", 0, 28)
  display_name = "Service Account for ${var.app_name}"
}

resource "google_service_account" "pubsub" {
  account_id   = "pubsub-invoker"
  display_name = "Cloud Run Pub/Sub Invoker"
}
