# Pega a última imagem oficial do Ubuntu 22.04 LTS
data "aws_ami" "ubuntu" {
  most_recent = true
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
  owners = ["099720109477"] #
}

resource "aws_instance" "app_server" {
  ami                  = data.aws_ami.ubuntu.id
  instance_type        = "t2.micro" # Elegível para o Free Tier (1 ano)
  security_groups      = [aws_security_group.ec2_sg.name]
  
  tags = {
    Name = var.project_name
  }

  user_data = <<-EOF
              #!/bin/bash
              apt-get update -y
              apt-get install -y docker.io git ffmpeg
              systemctl start docker
              systemctl enable docker
              usermod -aG docker ubuntu
              EOF
}