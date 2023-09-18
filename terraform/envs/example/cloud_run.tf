locals {
  image = var.container_image != "" ? var.container_image : "${google_artifact_registry_repository.repository.location}-docker.pkg.dev/${var.gcp_project_id}/${google_artifact_registry_repository.repository.name}/${var.app_name}:latest"
}

resource "google_cloud_run_v2_service" "api" {
  name     = "${var.app_name}-api"
  location = var.gcp_region
  ingress  = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"

  template {
    scaling {
      min_instance_count = 1
      max_instance_count = 3
    }

    service_account = google_service_account.app.email

    containers {
      image   = local.image
      command = var.container_command_api

      env {
        name  = "GOOGLE_PROJECT_ID"
        value = var.gcp_project_id
      }
      env {
        name  = "PUBSUB_GENERATE_ANNOTATIONS_TOPIC"
        value = google_pubsub_topic.main.name
      }
      env {
        name  = "CLOUD_STORAGE_BUCKET"
        value = google_storage_bucket.bucket.name
      }
      env {
        name  = "DATASTORE_DATABASE"
        value = google_firestore_database.database.name
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [module.enable_google_apis, google_firestore_database.database, google_pubsub_subscription.main, google_storage_bucket.bucket]
}

resource "google_cloud_run_v2_service" "worker" {
  name     = "${var.app_name}-worker"
  location = var.gcp_region
  ingress  = "INGRESS_TRAFFIC_INTERNAL_ONLY"

  template {
    scaling {
      min_instance_count = 1
      max_instance_count = 3
    }

    service_account = google_service_account.app.email

    containers {
      image   = local.image
      command = var.container_command_worker
      resources {
        limits = {
          cpu    = "1000m"
          memory = "1Gi"
        }
      }

      env {
        name  = "GOOGLE_PROJECT_ID"
        value = var.gcp_project_id
      }
      env {
        name  = "PUBSUB_GENERATE_ANNOTATIONS_TOPIC"
        value = google_pubsub_topic.main.name
      }
      env {
        name  = "CLOUD_STORAGE_BUCKET"
        value = google_storage_bucket.bucket.name
      }
      env {
        name  = "DATASTORE_DATABASE"
        value = google_firestore_database.database.name
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [module.enable_google_apis, google_firestore_database.database, google_storage_bucket.bucket]
}

resource "google_cloud_run_service_iam_member" "api_invoker" {
  location = google_cloud_run_v2_service.api.location
  project  = google_cloud_run_v2_service.api.project
  service  = google_cloud_run_v2_service.api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service_iam_member" "worker_invoker" {
  location = google_cloud_run_v2_service.worker.location
  project  = google_cloud_run_v2_service.worker.project
  service  = google_cloud_run_v2_service.worker.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.pubsub.email}"
}
