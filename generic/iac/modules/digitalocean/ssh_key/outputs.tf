output "id" {
  description = "The unique ID of the SSH key"
  value       = digitalocean_ssh_key.main.id
}

output "fingerprint" {
  description = "The fingerprint of the SSH key"
  value       = digitalocean_ssh_key.main.fingerprint
}

output "name" {
  description = "The name of the SSH key"
  value       = digitalocean_ssh_key.main.name
}

output "private_key_pem" {
  description = "The private key in PEM format (only available when generate_ssh_key is true)"
  value       = tls_private_key.main.private_key_pem
  sensitive   = true
}

output "private_key_openssh" {
  description = "The private key in OpenSSH format (only available when generate_ssh_key is true)"
  value       = tls_private_key.main.private_key_openssh
  sensitive   = true
}

output "public_key_openssh" {
  description = "The public key in OpenSSH format"
  value       = tls_private_key.main.public_key_openssh
}

output "public_key_pem" {
  description = "The public key in PEM format"
  value       = tls_private_key.main.public_key_pem
}