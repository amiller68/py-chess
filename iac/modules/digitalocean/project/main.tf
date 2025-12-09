resource "digitalocean_project" "project" {
  name        = var.name
  description = var.description
  purpose     = "Web Application"
  environment = var.environment
  resources   = var.resources
}