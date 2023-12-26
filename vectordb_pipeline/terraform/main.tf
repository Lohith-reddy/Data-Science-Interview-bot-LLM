provider "google" {
  project     = "griller-490718"
  region      = "us-central1"
}

resource "google_compute_instance" "data_eng_bastian" {
  name         = "data-eng-bastian"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-9"
    }
  }

  network_interface {
    network = "default"

    access_config {
      // Ephemeral IP
    }
  }

  service_account {
    scopes = ["cloud-platform"]
  }

  metadata = {
    ssh-keys = "username:${file("~/.ssh/id_rsa.pub")}"
  }
}