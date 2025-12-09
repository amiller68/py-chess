variable "name" {
  description = "The name of the droplet"
  type        = string
}

variable "description" {
  description = "The description of the project"
  type        = string
}

variable "environment" {
  description = "Environment name (staging, production, etc.)"
  type        = string
  validation {
    # supported environments
    # TODO: support more environments
    condition     = contains(["production"], var.environment)
    error_message = "Environment must be one of: production"
  }
}

variable "resources" {
  description = "Resources of the project"
  type        = list(string)
}
