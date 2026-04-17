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

variable "cluster_name" {
  type    = string
  default = "k8s-cluster"
}

variable "network_name" {
  type    = string
  default = "k8s-network"
}

variable "subnet_name" {
  type    = string
  default = "subnet-a"
}

variable "node_group_name" {
  type    = string
  default = "k8s-node-group"
}

variable "k8s_version" {
  type = string
}

variable "sa_name" {
  type = string
}

variable "subnet_cidr" {
  type    = string
  default = "10.1.0.0/16"
}

variable "cluster_ipv4_cidr" {
  type    = string
  default = "10.112.0.0/16"
}

variable "service_ipv4_cidr" {
  type    = string
  default = "10.96.0.0/16"
}

variable "api_allowed_cidrs" {
  type        = list(string)
  default     = []
  description = "CIDR ranges allowed to access the Kubernetes API."
}

variable "ssh_allowed_cidrs" {
  type        = list(string)
  default     = []
  description = "CIDR ranges allowed to connect to cluster nodes over SSH."
}

variable "node_service_allowed_cidrs" {
  type        = list(string)
  default     = ["0.0.0.0/0"]
  description = "CIDR ranges allowed to access NodePort services."
}

variable "node_cores" {
  type    = number
  default = 2
}

variable "node_memory" {
  type    = number
  default = 4
}

variable "node_disk_size" {
  type    = number
  default = 64
}

variable "node_count" {
  type    = number
  default = 2
}
