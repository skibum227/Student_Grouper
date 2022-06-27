# Only running one thing so this is set to an empty string for symplicity
variable "resource_prefix" {
  description = "Used as a prefix for all resources in a module - make sure to add a hyphen"
  type        = string
  default     = ""
}
