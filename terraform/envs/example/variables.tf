##########################################
# Project, region and zone
##########################################

variable "gcp_project_id" {
  description = "Project id where app will be deployed"
  type        = string
}

variable "gcp_region" {
  description = "Region of the components"
  type        = string
  default     = "europe-west1"
}

variable "gcp_zone" {
  description = "Zone of the components"
  type        = string
  default     = "europe-west1-b"
}

variable "datastore_location" {
  description = "Location of the datastore"
  type        = string
  default     = "europe-west2"
}

##########################################
# Application
##########################################

variable "app_name" {
  description = "Short app name without spaces or underscores"
  type        = string
  default     = "thumbnails-generation"
}

variable "main_subscription_url_path" {
  description = "URL path for the main subscription"
  type        = string
  default     = "/generate_thumbnails"
}

variable "main_subscription_dead_letter_url_path" {
  description = "URL path for the main subscription"
  type        = string
  default     = "/generate_thumbnails_dlq"
}


##########################################
# Cloud Run
##########################################

variable "container_image" {
  description = "Container image to deploy, must be in the same project as the app or public. If not specified, a default image will be used"
  type        = string
  default     = ""
}

variable "container_command_api" {
  description = "Command to run during the container startup"
  type        = list(string)
  default     = ["/start_api"]
}

variable "container_command_worker" {
  description = "Command to run during the container startup"
  type        = list(string)
  default     = ["/start_worker"]
}
