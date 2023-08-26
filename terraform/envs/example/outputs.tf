output "container_image" {
  value = local.image
}

output "load_balancer_address" {
  value = "http://${google_compute_global_address.global-static-ip.address}"
}
