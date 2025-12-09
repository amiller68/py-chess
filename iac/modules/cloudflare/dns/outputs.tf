output "zone_id" {
  description = "The Cloudflare Zone ID"
  value       = data.cloudflare_zone.main.id
}

output "zone_name" {
  description = "The Cloudflare Zone name"
  value       = data.cloudflare_zone.main.name
}

output "subdomain_records" {
  description = "Map of subdomain records with their IDs and hostnames"
  value = {
    for slug, record in cloudflare_record.subdomains : slug => {
      id       = record.id
      hostname = record.hostname
    }
  }
}