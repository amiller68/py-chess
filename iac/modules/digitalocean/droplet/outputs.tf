output "id" {
  description = "The ID of the droplet"
  value       = digitalocean_droplet.main.id
}

output "urn" {
  description = "The uniform resource name of the droplet"
  value       = digitalocean_droplet.main.urn
}

output "name" {
  description = "The name of the droplet"
  value       = digitalocean_droplet.main.name
}

output "region" {
  description = "The region of the droplet"
  value       = digitalocean_droplet.main.region
}

output "image" {
  description = "The image of the droplet"
  value       = digitalocean_droplet.main.image
}

output "ipv4_address" {
  description = "The public IPv4 address of the droplet"
  value       = digitalocean_droplet.main.ipv4_address
}

output "ipv4_address_private" {
  description = "The private IPv4 address of the droplet"
  value       = digitalocean_droplet.main.ipv4_address_private
}

output "ipv6_address" {
  description = "The public IPv6 address of the droplet"
  value       = digitalocean_droplet.main.ipv6_address
}

output "status" {
  description = "The status of the droplet"
  value       = digitalocean_droplet.main.status
}

output "tags" {
  description = "The tags of the droplet"
  value       = digitalocean_droplet.main.tags
}

output "firewall_id" {
  description = "The ID of the firewall"
  value       = digitalocean_firewall.main.id
}