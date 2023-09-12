##########################################
# Service Accounts
##########################################

resource "google_service_account" "app" {
  account_id   = "${var.app_name}-sa"
  display_name = "Service Account for ${var.app_name}"
}

resource "google_service_account" "pubsub" {
  account_id   = "pubsub-invoker"
  display_name = "Cloud Run Pub/Sub Invoker"
}

##########################################
# Bucket IAM Members
##########################################

resource "google_storage_bucket_iam_member" "app_sa_main_bucket_admin" {
  bucket = google_storage_bucket.main.name
  role   = "roles/storage.admin"
  member = "serviceAccount:${google_service_account.app.email}"
}

resource "google_storage_bucket_iam_member" "service_sa_dead_letter_bucket_admin" {
  bucket = google_storage_bucket.dead_letter.name
  role   = "roles/storage.admin"
  member = "serviceAccount:service-${data.google_project.default.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

##########################################
# PubSub IAM Members
##########################################

resource "google_pubsub_subscription_iam_member" "app_sa_main_subscription_subscriber" {
  subscription = google_pubsub_subscription.main.name
  role         = "roles/pubsub.subscriber"
  member       = "serviceAccount:${google_service_account.app.email}"
}

resource "google_pubsub_topic_iam_member" "app_sa_main_topic_publisher" {
  topic  = google_pubsub_topic.main.name
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:${google_service_account.app.email}"
}
