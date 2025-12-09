variable "name" {
  description = "The name of the SSH key"
  type        = string
}

variable "generate_ssh_key" {
  description = "Whether to generate a new SSH key pair"
  type        = bool
  default     = true
}

variable "public_key" {
  description = "The public key content (required if generate_ssh_key is false)"
  type        = string
  default     = ""
}

variable "key_algorithm" {
  description = "The algorithm to use for key generation (RSA or ECDSA)"
  type        = string
  default     = "RSA"
  
  validation {
    condition     = contains(["RSA", "ECDSA"], var.key_algorithm)
    error_message = "Key algorithm must be either RSA or ECDSA"
  }
}

variable "rsa_bits" {
  description = "The size of the RSA key in bits"
  type        = number
  default     = 4096
  
  validation {
    condition     = contains([2048, 3072, 4096], var.rsa_bits)
    error_message = "RSA bits must be 2048, 3072, or 4096"
  }
}

variable "ecdsa_curve" {
  description = "The ECDSA curve to use"
  type        = string
  default     = "P256"
  
  validation {
    condition     = contains(["P224", "P256", "P384", "P521"], var.ecdsa_curve)
    error_message = "ECDSA curve must be P224, P256, P384, or P521"
  }
}