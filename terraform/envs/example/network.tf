resource "google_compute_region_network_endpoint_group" "api_neg" {
  name                  = "neg-${var.app_name}"
  network_endpoint_type = "SERVERLESS"
  region                = var.gcp_region
  cloud_run {
    service = google_cloud_run_v2_service.api.name
  }

  depends_on = [module.enable_google_apis]
}

resource "google_compute_backend_service" "default" {
  name = "be-${var.app_name}"

  backend {
    group = google_compute_region_network_endpoint_group.api_neg.id
  }
}

resource "google_compute_global_address" "global-static-ip" {
  name = "global-static-ip"
}

module "service_loadbalancer" {
  source  = "GoogleCloudPlatform/lb-http/google//modules/serverless_negs"
  version = "~> 6.0"
  name    = "${var.app_name}-service"
  project = var.gcp_project_id

  address        = google_compute_global_address.global-static-ip.address
  create_address = false
  ssl            = false
  create_url_map = true

  backends = {
    default = {
      description = null
      groups = [
        {
          group = google_compute_region_network_endpoint_group.api_neg.id
        }
      ]
      enable_cdn              = false
      custom_request_headers  = null
      custom_response_headers = null
      security_policy         = null

      iap_config = {
        enable               = false
        oauth2_client_id     = ""
        oauth2_client_secret = ""
      }
      log_config = {
        enable      = false
        sample_rate = null
      }
    }
  }
}
