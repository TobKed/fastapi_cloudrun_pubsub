locals {
  github_actions_oidc_enabled = can(var.oidc_github_repository) && length(var.oidc_github_repository) > 0
  github_actions_account_roles = [
    "roles/artifactregistry.writer",
  ]
}

resource "google_service_account" "github_actions_sa" {
  count        = local.github_actions_oidc_enabled ? 1 : 0
  account_id   = "githubactions-sa-tf"
  display_name = "githubactions-sa-tf"
}

resource "google_project_iam_member" "github_actions_account_role_binding" {
  for_each = local.github_actions_oidc_enabled ? toset(local.github_actions_account_roles) : toset([])
  project  = var.gcp_project_id
  role     = each.value
  member   = "serviceAccount:${google_service_account.github_actions_sa[0].email}"
}

module "github_actions_oidc" {
  count  = local.github_actions_oidc_enabled ? 1 : 0
  source = "../../modules/github_actions_oidc"

  gcp_project_id = var.gcp_project_id

  github_repositories               = [var.oidc_github_repository]
  github_actions_service_account_id = google_service_account.github_actions_sa[0].id

  depends_on = [google_project_iam_member.github_actions_account_role_binding]
}
