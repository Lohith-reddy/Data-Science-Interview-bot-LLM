variable "master_count" {
  description = "The number of master nodes"
  type        = number
  default     = 1
}

variable "worker_count" {
  description = "The number of worker nodes"
  type        = number
  default     = 1
}