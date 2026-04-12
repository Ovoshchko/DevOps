data "yandex_compute_image" "ubuntu" {
  family = var.image_family
}

resource "yandex_vpc_network" "network" {
  name = "traffic-analyzer-network"
}

resource "yandex_vpc_subnet" "subnet" {
  name           = "traffic-analizer-subnet"
  network_id     = yandex_vpc_network.network.id
  zone           = var.zone
  v4_cidr_blocks = var.subnet_cidr
}

locals {
  ssh_key = file(var.ssh_public_key_path)
}

resource "yandex_compute_instance" "vm" {
  name        = var.vm_name
  platform_id = var.platform_id

  lifecycle {
    create_before_destroy = true
  }

  resources {
    cores  = var.cores
    memory = var.memory
  }

  boot_disk {
    initialize_params {
      image_id = data.yandex_compute_image.ubuntu.image_id
      size     = var.disk_size
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.subnet.id
    nat       = true
  }

  metadata = {
    ssh-keys = "ubuntu:${file("~/.ssh/id_ed25519.pub")}"
  }
}