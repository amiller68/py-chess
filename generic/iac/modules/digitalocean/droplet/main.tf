resource "digitalocean_droplet" "main" {
  name     = var.name
  region   = var.region
  size     = var.size
  image    = var.image
  
  ssh_keys = var.ssh_keys
  
  vpc_uuid = var.vpc_uuid
  
  tags = concat(
    var.tags,
    ["dockerized-service"]
  )
  
  monitoring         = var.monitoring
  backups           = var.backups
  ipv6              = var.ipv6
  resize_disk       = var.resize_disk
  droplet_agent     = var.droplet_agent
  graceful_shutdown = var.graceful_shutdown
}

resource "digitalocean_firewall" "main" {
  name = "${var.name}-firewall"
  
  droplet_ids = [digitalocean_droplet.main.id]
  
  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = var.ssh_allowed_ips
  }
  
  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }
  
  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }
  
  dynamic "inbound_rule" {
    for_each = var.additional_ports
    content {
      protocol         = "tcp"
      port_range       = inbound_rule.value
      source_addresses = ["0.0.0.0/0", "::/0"]
    }
  }
  
  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
  
  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
  
  outbound_rule {
    protocol              = "icmp"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}