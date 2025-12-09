# Production Infrastructure - Digital Ocean Droplet for py-chess

locals {
  environment = "production"
}

module "common" {
  source = "../../modules/common"

  project_name = var.project_name
  environment  = local.environment
  subdomains   = var.subdomains
  digitalocean = {
    droplet = {
      region = "nyc3"
    }
  }
  cloudflare = {
    ttl           = 300
    proxied       = false
    dns_root_zone = var.dns_root_zone
  }
}
