output "vpc_id" {
  value = aws_vpc.main.id
}

output "public_subnet_id" {
  value = aws_subnet.public.id
}

output "security_group_id" {
  value = aws_security_group.rhel_sg.id
}

output "instance_id" {
  value = aws_instance.rhel_server.id
}

output "instance_public_ip" {
  value = aws_instance.rhel_server.public_ip
}

output "ssh_command" {
  value = "ssh -i <your-private-key.pem> ec2-user@${aws_instance.rhel_server.public_ip}"
}