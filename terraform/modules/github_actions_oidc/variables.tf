variable "gcp_project_id" {
  type = string
}

variable "github_repositories" {
  type = list(string)
}

variable "github_actions_service_account_id" {
  type = string
}

variable "workload_identity_pool_id" {
  type    = string
  default = "github-actions-pool"
}

variable "workload_identity_pool_provider_id" {
  type    = string
  default = "github-actions-pool-provider"
}
