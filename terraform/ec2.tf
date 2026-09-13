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
  owners = ["099720109477"] # Canonical
}

# Criação da Instância EC2
resource "aws_instance" "app_server" {
  ami                  = data.aws_ami.ubuntu.id
  
  # Usando t3.xlarge (16 GB de RAM) para suportar o Llama 3.1 na nuvem.
  # Se preferir uma com GPU (mais cara e rápida), altere para "g4dn.xlarge", momento usando sem GPU só na RAM
  instance_type        = "t3.xlarge" 
  
  security_groups      = [aws_security_group.ec2_sg.name]
  
  tags = {
    Name = var.project_name
  }

  # Script executado automaticamente no primeiro boot da máquina
  user_data = <<-EOF
              #!/bin/bash
              apt-get update -y
              apt-get install -y docker.io git ffmpeg curl
              
              # Configura o Docker para iniciar com o sistema
              systemctl start docker
              systemctl enable docker
              usermod -aG docker ubuntu

              # Instala o Ollama de forma automatizada na EC2
              curl -fsSL https://ollama.com/install.sh | sh

              # Inicia o serviço do Ollama e baixa o modelo Llama 3.1 em segundo plano
              ollama serve &
              sleep 5
              ollama pull llama3.1
              EOF
}