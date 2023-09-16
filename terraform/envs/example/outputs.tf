output "google_storage_bucket" {
  value = google_storage_bucket.bucket.name
}

output "container_image" {
  value = local.image
}

output "load_balancer_address" {
  value = "http://${google_compute_global_address.global-static-ip.address}"
}

output "github_actions_workload_identity_pool_provider" {
  value = module.github_actions_oidc.google_iam_workload_identity_pool_provider
}

output "github_actions_service_account" {
  value = google_service_account.github_actions_sa.email
}
