locals {
  github_actions_account_roles = toset([
    "roles/artifactregistry.writer",
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
