resource "random_id" "server_suffix" {
  byte_length = 3
}

# Generate strong random passwords for MariaDB
resource "random_password" "db_password" {
  length  = 24
  special = false
}

resource "random_password" "mysql_root_password" {
  length  = 24
  special = false
}

# Generate RSA 4096-bit SSH Key Pair automatically
resource "tls_private_key" "snipeit_ssh" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "snipeit_keypair" {
  key_name   = "snipeit-key-${random_id.server_suffix.hex}"
  public_key = tls_private_key.snipeit_ssh.public_key_openssh

  tags = {
    Project = "Snipe-IT Asset Management"
  }
}

# Save the private key locally as snipeit-key.pem with 0600 permissions
resource "local_file" "private_key_file" {
  content         = tls_private_key.snipeit_ssh.private_key_pem
  filename        = "${path.module}/snipeit-key.pem"
  file_permission = "0600"
}

# Security Group allowing SSH (22), Snipe-IT Portal (8000), HTTP (80), HTTPS (443)
resource "aws_security_group" "snipeit_sg" {
  name        = "snipeit-sg-${random_id.server_suffix.hex}"
  description = "Security group for Snipe-IT ITAM portal and SSH management"

  ingress {
    description = "SSH access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  ingress {
    description = "Snipe-IT Web Interface"
    from_port   = var.app_port
    to_port     = var.app_port
    protocol    = "tcp"
    cidr_blocks = [var.allowed_http_cidr]
  }

  ingress {
    description = "Standard HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [var.allowed_http_cidr]
  }

  ingress {
    description = "Standard HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.allowed_http_cidr]
  }

  egress {
    description = "Allow all outbound traffic for container pulls and OS updates"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "snipeit-sg"
    Project = "Snipe-IT Asset Management"
  }
}

# Fetch latest Ubuntu 24.04 LTS official AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Deploy EC2 Instance
resource "aws_instance" "snipeit_server" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  key_name                    = aws_key_pair.snipeit_keypair.key_name
  vpc_security_group_ids      = [aws_security_group.snipeit_sg.id]
  associate_public_ip_address = true

  root_block_device {
    volume_size           = var.volume_size
    volume_type           = "gp3"
    delete_on_termination = true
    tags = {
      Name = "snipeit-disk"
    }
  }

  user_data = templatefile("${path.module}/user_data.sh.tpl", {
    app_port            = var.app_port
    timezone            = var.timezone
    db_database         = var.db_database
    db_username         = var.db_username
    db_password         = random_password.db_password.result
    mysql_root_password = random_password.mysql_root_password.result
    mail_mailer         = var.mail_mailer
    mail_host           = var.mail_host
    mail_port           = var.mail_port
    mail_username       = var.mail_username
    mail_password       = var.mail_password
    mail_encryption     = var.mail_encryption
  })

  tags = {
    Name    = "snipeit-server"
    Project = "Snipe-IT Asset Management"
  }
}
