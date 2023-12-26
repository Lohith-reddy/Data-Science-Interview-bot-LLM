provider "google" {
  project = "griller-490718"
  region  = "us-central1"
}

resource "google_compute_instance" "master" {
  count        = var.master_count
  name         = "master-${count.index}"
  machine_type = "e2-small"
  zone         = "us-central1-a"
  tags         = ["griller_cluster"]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-9"
    }
  }

  network_interface {
    network = "k8cluster"

    access_config {
      // Ephemeral IP
    }
  }
}

resource "google_compute_instance" "worker" {
  count        = var.worker_count
  name         = "worker-${count.index}"
  machine_type = "e2-micro"
  zone         = "us-central1-a"
  tags         = ["griller_cluster"]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-9"
    }
  }

  network_interface {
    network = "k8cluster"

    access_config {
      // Ephemeral IP
    }
  }
}

resource "google_compute_firewall" "allow_http" {
  name    = "allow-http"
  network = "k8cluster"

  allow {
    protocol = "tcp"
    ports    = ["80"]
  }

  source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_firewall" "allow_ssh_from_bastion" {
  name    = "allow-ssh-from-bastion"
  network = "k8cluster"

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["${google_compute_instance.griller_bastion.network_interface.0.access_config.0.nat_ip}/32"]
}