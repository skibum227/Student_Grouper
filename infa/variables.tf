variable "name" {
  description = "the name of your stack, e.g. \"demo\""
  default = "student-grouper"
}

variable "resource_prefix" {
  description = "Used as a prefix for all resources in a module."
  type        = string
  default     = "testing"
}
