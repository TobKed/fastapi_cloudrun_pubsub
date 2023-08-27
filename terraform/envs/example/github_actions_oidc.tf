locals {
  github_actions_account_roles = toset([
    #    "roles/run.developer",
    "roles/artifactregistry.writer",
    #    "roles/storage.objectViewer",
  ])

  service_accounts_to_impersonate_by_gh_actions = toset([
    data.google_compute_default_service_account.default.name,
  ])
}

resource "google_service_account" "github_actions_sa" {
  account_id   = "githubactions-sa-tf"
  display_name = "githubactions-sa-tf"
}

resource "google_project_iam_member" "github_actions_account_role_binding" {
  for_each = local.github_actions_account_roles
  project  = var.gcp_project_id
  role     = each.value
  member   = "serviceAccount:${google_service_account.github_actions_sa.email}"
}

module "github_actions_oidc" {
  source = "../../modules/github_actions_oidc"

  gcp_project_id = var.gcp_project_id

  github_repositories               = [var.oidc_github_repository]
  github_actions_service_account_id = google_service_account.github_actions_sa.id
}

#resource "google_service_account_iam_binding" "service_accounts_to_github_actions_iam_binding" {
#  for_each           = local.service_accounts_to_impersonate_by_gh_actions
#  service_account_id = each.key
#  role               = "roles/iam.serviceAccountUser"
#
#  members = [
#    "serviceAccount:${google_service_account.github_actions_sa.email}",
#  ]
#}
