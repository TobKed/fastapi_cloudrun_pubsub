resource "google_pubsub_topic" "main" {
  name = var.app_name

  depends_on = [module.enable_google_apis]
}

resource "google_pubsub_topic" "main_dead_letter" {
  name = "${google_pubsub_topic.main.name}-dlq"

  depends_on = [module.enable_google_apis]
}

resource "google_pubsub_subscription" "main" {
  name  = "${var.app_name}-sub"
  topic = google_pubsub_topic.main.name

  # https://cloud.google.com/run/docs/triggering/pubsub-push#ack-deadline
  ack_deadline_seconds = 599

  # 20 minutes
  message_retention_duration = "1200s"

  expiration_policy {
    ttl = ""
  }
  retry_policy {
    minimum_backoff = "10s"
  }

  enable_message_ordering = false

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.main_dead_letter.id
    max_delivery_attempts = 5
  }

  push_config {
    push_endpoint = "${google_cloud_run_v2_service.worker.uri}${var.main_subscription_url_path}"
    oidc_token {
      service_account_email = google_service_account.pubsub.email
    }
    attributes = {
      x-goog-version = "v1"
    }
  }
}

resource "google_pubsub_subscription" "main_dead_letter" {
  name  = "${google_pubsub_subscription.main.name}-dlq"
  topic = google_pubsub_topic.main_dead_letter.name

  cloud_storage_config {
    bucket = google_storage_bucket.dead_letter.name
    avro_config {
      write_metadata = true
    }
  }
  depends_on = [
    google_storage_bucket.dead_letter,
    google_storage_bucket_iam_member.service_sa_dead_letter_bucket_admin,
  ]
}
