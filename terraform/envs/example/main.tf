terraform {
  required_version = ">= 1.5"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.66.0"
    }
  }

  # to store state on the bucket you can use the following backend
  #  backend "gcs" {
  #    bucket = "your-project-bucket-for-terraform"
  #    prefix = "terraform/state/dev"
  #  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
  zone    = var.gcp_zone
}

data "google_project" "default" {}

data "google_compute_default_service_account" "default" {
  depends_on = [module.enable_google_apis]
}


module "enable_google_apis" {
  source  = "terraform-google-modules/project-factory/google//modules/project_services"
  version = "~> 14.0"

  project_id                  = var.gcp_project_id
  disable_services_on_destroy = false
  disable_dependent_services  = false

  activate_apis = [
    "artifactregistry.googleapis.com",
    "compute.googleapis.com",
    "firestore.googleapis.com",
    "iamcredentials.googleapis.com",
    "pubsub.googleapis.com",
    "run.googleapis.com",
  ]
}
