variable "aws_region" {
  description = "AWS Region to deploy resources"
  type        = string
  default     = "ap-south-1" # Asia Pacific (Mumbai)
}

variable "instance_type" {
  description = "EC2 Instance type (t3.micro or t2.micro for AWS Free Tier)"
  type        = string
  default     = "t3.micro"
}

variable "volume_size" {
  description = "Root EBS storage size in GB (gp3)"
  type        = number
  default     = 20
}

variable "app_port" {
  description = "Web port on which Snipe-IT UI will be served"
  type        = number
  default     = 8000
}

variable "timezone" {
  description = "Application timezone for Snipe-IT"
  type        = string
  default     = "Asia/Kolkata"
}

variable "db_database" {
  description = "MariaDB database name for Snipe-IT"
  type        = string
  default     = "snipeit"
}

variable "db_username" {
  description = "MariaDB username for Snipe-IT"
  type        = string
  default     = "snipeit"
}

variable "allowed_ssh_cidr" {
  description = "CIDR block allowed for SSH access"
  type        = string
  default     = "0.0.0.0/0"
}

variable "allowed_http_cidr" {
  description = "CIDR block allowed for Snipe-IT web portal access"
  type        = string
  default     = "0.0.0.0/0"
}

variable "mail_mailer" {
  description = "Mail driver: 'log' for file logging or 'smtp' for email delivery"
  type        = string
  default     = "log"
}

variable "mail_host" {
  description = "SMTP host (e.g. smtp.gmail.com)"
  type        = string
  default     = "smtp.gmail.com"
}

variable "mail_port" {
  description = "SMTP port (e.g. 587 for TLS)"
  type        = number
  default     = 587
}

variable "mail_username" {
  description = "SMTP username / Gmail address"
  type        = string
  default     = ""
}

variable "mail_password" {
  description = "SMTP password / Gmail 16-character App Password"
  type        = string
  default     = ""
  sensitive   = true
}

variable "mail_encryption" {
  description = "SMTP encryption (tls or ssl)"
  type        = string
  default     = "tls"
}
