variable "user_emails" {
  description = "The user email for IAP"
  type        = list(string)
  default     = []
}

variable "projectid" {
  description = "The project ID"
  type        = string
  default     = "griller-490718"
}

variable "zone" {
  description = "The zone"
  type        = string
  default     = "us-central1-a"
}