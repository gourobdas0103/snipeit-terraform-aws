output "instance_id" {
  description = "AWS EC2 Instance ID"
  value       = aws_instance.snipeit_server.id
}

output "ec2_public_ip" {
  description = "Public IPv4 address of the Snipe-IT server"
  value       = aws_instance.snipeit_server.public_ip
}

output "snipeit_web_url" {
  description = "Direct Web URL to access Snipe-IT ITAM Portal"
  value       = "http://${aws_instance.snipeit_server.public_ip}:${var.app_port}"
}

output "ssh_command" {
  description = "SSH command to connect to your server"
  value       = "ssh -i ${local_file.private_key_file.filename} ubuntu@${aws_instance.snipeit_server.public_ip}"
}

output "cloud_init_log_command" {
  description = "Command to stream provisioning logs in real-time"
  value       = "ssh -i ${local_file.private_key_file.filename} ubuntu@${aws_instance.snipeit_server.public_ip} 'tail -f /var/log/snipeit-cloudinit.log'"
}

output "db_database" {
  description = "MariaDB Database Name"
  value       = var.db_database
}

output "db_username" {
  description = "MariaDB Database User"
  value       = var.db_username
}

output "db_password" {
  description = "Auto-generated secure MariaDB User Password"
  value       = random_password.db_password.result
  sensitive   = true
}

output "mysql_root_password" {
  description = "Auto-generated secure MySQL Root Password"
  value       = random_password.mysql_root_password.result
  sensitive   = true
}
