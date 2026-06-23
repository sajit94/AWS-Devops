aws_region         = "ap-southeast-2"
project_name       = "test-rhel"
vpc_cidr           = "10.0.0.0/16"
public_subnet_cidr = "10.0.1.0/24"
availability_zone  = "ap-southeast-2a"

ssh_allowed_cidr   = "49.205.206.201/32"

rhel_ami_id        = " ami-0d432cb7e26535aa3 |"
instance_type      = "t3.micro"

key_name           = "gitlab"