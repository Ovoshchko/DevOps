# Infrastructure for Yandex Cloud Managed Service for Kubernetes cluster

resource "yandex_vpc_network" "k8s-network" {
  description = "Network for the Managed Service for Kubernetes cluster"
  name        = var.network_name
}

resource "yandex_vpc_subnet" "subnet-a" {
  description    = "Subnet in the cluster availability zone"
  name           = var.subnet_name
  zone           = var.zone
  network_id     = yandex_vpc_network.k8s-network.id
  v4_cidr_blocks = [var.subnet_cidr]
}

resource "yandex_vpc_security_group" "k8s-cluster-nodegroup-traffic" {
  description = "Service traffic between the cluster and node groups"
  name        = "k8s-cluster-nodegroup-traffic"
  network_id  = yandex_vpc_network.k8s-network.id

  ingress {
    description       = "Health checks for network load balancers"
    from_port         = 0
    to_port           = 65535
    protocol          = "TCP"
    predefined_target = "loadbalancer_healthchecks"
  }

  ingress {
    description       = "Traffic between the control plane and nodes"
    from_port         = 0
    to_port           = 65535
    protocol          = "ANY"
    predefined_target = "self_security_group"
  }

  ingress {
    description    = "ICMP checks from the cluster subnet"
    protocol       = "ICMP"
    v4_cidr_blocks = [var.subnet_cidr]
  }

  egress {
    description       = "Traffic between the control plane and nodes"
    from_port         = 0
    to_port           = 65535
    protocol          = "ANY"
    predefined_target = "self_security_group"
  }
}

resource "yandex_vpc_security_group" "k8s-nodegroup-traffic" {
  description = "Service traffic for the node groups"
  name        = "k8s-nodegroup-traffic"
  network_id  = yandex_vpc_network.k8s-network.id

  ingress {
    description    = "Traffic between pods and services"
    from_port      = 0
    to_port        = 65535
    protocol       = "ANY"
    v4_cidr_blocks = [var.cluster_ipv4_cidr, var.service_ipv4_cidr]
  }

  egress {
    description    = "Outbound Internet access for nodes"
    from_port      = 0
    to_port        = 65535
    protocol       = "ANY"
    v4_cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "yandex_vpc_security_group" "k8s-services-access" {
  name        = "k8s-services-access"
  description = "Access to Kubernetes NodePort services"
  network_id  = yandex_vpc_network.k8s-network.id

  ingress {
    description    = "Access to NodePort services"
    from_port      = 30000
    to_port        = 32767
    protocol       = "TCP"
    v4_cidr_blocks = var.node_service_allowed_cidrs
  }
}

resource "yandex_vpc_security_group" "k8s-ssh-access" {
  description = "Optional SSH access to cluster nodes"
  name        = "k8s-ssh-access"
  network_id  = yandex_vpc_network.k8s-network.id

  dynamic "ingress" {
    for_each = length(var.ssh_allowed_cidrs) == 0 ? [] : [1]

    content {
      description    = "SSH access to cluster nodes"
      port           = 22
      protocol       = "TCP"
      v4_cidr_blocks = var.ssh_allowed_cidrs
    }
  }
}

resource "yandex_vpc_security_group" "k8s-cluster-traffic" {
  description = "Traffic rules for the Kubernetes control plane"
  name        = "k8s-cluster-traffic"
  network_id  = yandex_vpc_network.k8s-network.id

  dynamic "ingress" {
    for_each = length(var.api_allowed_cidrs) == 0 ? [] : [443, 6443]

    content {
      description    = "Access to the Kubernetes API"
      port           = ingress.value
      protocol       = "TCP"
      v4_cidr_blocks = var.api_allowed_cidrs
    }
  }

  egress {
    description    = "Traffic between the control plane and metric-server pods"
    port           = 4443
    protocol       = "TCP"
    v4_cidr_blocks = [var.cluster_ipv4_cidr]
  }
}

resource "yandex_iam_service_account" "k8s-sa" {
  name = var.sa_name
}

resource "yandex_resourcemanager_folder_iam_binding" "k8s-clusters-agent" {
  folder_id = var.folder_id
  role      = "k8s.clusters.agent"
  members = [
    "serviceAccount:${yandex_iam_service_account.k8s-sa.id}"
  ]
}

resource "yandex_resourcemanager_folder_iam_binding" "k8s-tunnelClusters-agent" {
  folder_id = var.folder_id
  role      = "k8s.tunnelClusters.agent"
  members = [
    "serviceAccount:${yandex_iam_service_account.k8s-sa.id}"
  ]
}

resource "yandex_resourcemanager_folder_iam_binding" "vpc-publicAdmin" {
  folder_id = var.folder_id
  role      = "vpc.publicAdmin"
  members = [
    "serviceAccount:${yandex_iam_service_account.k8s-sa.id}"
  ]
}

resource "yandex_resourcemanager_folder_iam_binding" "images-puller" {
  folder_id = var.folder_id
  role      = "container-registry.images.puller"
  members = [
    "serviceAccount:${yandex_iam_service_account.k8s-sa.id}"
  ]
}

resource "yandex_resourcemanager_folder_iam_binding" "lb-admin" {
  folder_id = var.folder_id
  role      = "load-balancer.admin"
  members = [
    "serviceAccount:${yandex_iam_service_account.k8s-sa.id}"
  ]
}

resource "yandex_kubernetes_cluster" "k8s-cluster" {
  description        = "Managed Service for Kubernetes cluster"
  name               = var.cluster_name
  network_id         = yandex_vpc_network.k8s-network.id
  cluster_ipv4_range = var.cluster_ipv4_cidr
  service_ipv4_range = var.service_ipv4_cidr

  master {
    version = var.k8s_version

    master_location {
      zone      = yandex_vpc_subnet.subnet-a.zone
      subnet_id = yandex_vpc_subnet.subnet-a.id
    }

    public_ip = true

    security_group_ids = [
      yandex_vpc_security_group.k8s-cluster-nodegroup-traffic.id,
      yandex_vpc_security_group.k8s-cluster-traffic.id
    ]
  }

  service_account_id      = yandex_iam_service_account.k8s-sa.id
  node_service_account_id = yandex_iam_service_account.k8s-sa.id

  depends_on = [
    yandex_resourcemanager_folder_iam_binding.k8s-clusters-agent,
    yandex_resourcemanager_folder_iam_binding.k8s-tunnelClusters-agent,
    yandex_resourcemanager_folder_iam_binding.vpc-publicAdmin,
    yandex_resourcemanager_folder_iam_binding.images-puller,
    yandex_resourcemanager_folder_iam_binding.lb-admin
  ]
}

resource "yandex_kubernetes_node_group" "k8s-node-group" {
  description = "Node group for Managed Service for Kubernetes cluster"
  name        = var.node_group_name
  cluster_id  = yandex_kubernetes_cluster.k8s-cluster.id
  version     = var.k8s_version

  scale_policy {
    fixed_scale {
      size = var.node_count
    }
  }

  allocation_policy {
    location {
      zone = var.zone
    }
  }

  instance_template {
    platform_id = "standard-v2"

    network_interface {
      nat        = true
      subnet_ids = [yandex_vpc_subnet.subnet-a.id]
      security_group_ids = [
        yandex_vpc_security_group.k8s-cluster-nodegroup-traffic.id,
        yandex_vpc_security_group.k8s-nodegroup-traffic.id,
        yandex_vpc_security_group.k8s-services-access.id,
        yandex_vpc_security_group.k8s-ssh-access.id,
      ]
    }

    resources {
      memory = var.node_memory
      cores  = var.node_cores
    }

    boot_disk {
      type = "network-hdd"
      size = var.node_disk_size
    }
  }
}
