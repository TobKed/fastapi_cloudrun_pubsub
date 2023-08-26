resource "google_firestore_database" "database" {
  project                     = var.gcp_project_id
  name                        = "datastore-mode-database"
  location_id                 = var.datastore_location
  type                        = "DATASTORE_MODE"
  concurrency_mode            = "OPTIMISTIC"
  app_engine_integration_mode = "DISABLED"

  depends_on = [module.enable_google_apis]
}

resource "google_project_iam_member" "datastore" {
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.app.email}"
  project = var.gcp_project_id
}
