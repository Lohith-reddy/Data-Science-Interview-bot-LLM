resource "google_compute_instance" "bastion" {
  name         = "griller_bastion"
  machine_type = "e2-micro"
  zone         = var.zone
  tags         = ["griller_bastion"]
  project      = var.projectid

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-9"
    }
  }

  network_interface {
    network = "bastian"

    access_config {
      // Ephemeral IP
    }
  }
}

resource "google_compute_firewall" "bastion_allow_iap" {
  name    = "bastion-allow-iap"
  network = "bastian"
  project = var.projectid

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["35.235.240.0/20", "35.235.240.0/20"]
  target_tags   = ["bastion"]
}

resource "google_compute_firewall" "bastion_to_cluster" {
  name    = "bastion-to-cluster"
  network = "bastian"

  allow {
    protocol = "icmp"
  }

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  source_tags   = ["griller_bastion"]
  target_tags   = ["griller_cluster"]
}

resource "google_iap_tunnel_instance_iam_binding" "bastion" {
  project = var.projectid
  zone    = var.zone
  instance = google_compute_instance.bastion.name
  role    = "roles/iap.tunnelResourceAccessor"

  members = [for email in var.user_emails : "user:${email}"]
}