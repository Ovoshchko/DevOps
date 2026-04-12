variable "token" {
  type      = string
  sensitive = true
}

variable "cloud_id" {
  type = string
}

variable "folder_id" {
  type = string
}

variable "zone" {
  type    = string
  default = "ru-central1-a"
}

variable "vm_name" {
  type    = string
  default = "traffic-analyzer"
}

variable "platform_id" {
  type    = string
  default = "standard-v1"
}

variable "cores" {
  type    = number
  default = 2
}

variable "memory" {
  type    = number
  default = 2
}

variable "disk_size" {
  type    = number
  default = 20
}

variable "image_family" {
  type    = string
  default = "ubuntu-2204-lts"
}

variable "subnet_cidr" {
  type    = list(string)
  default = ["10.0.1.0/24"]
}

variable "ssh_public_key_path" {
  type    = string
  default = "~/.ssh/id_ed25519.pub"
}