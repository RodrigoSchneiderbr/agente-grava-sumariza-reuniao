

output "instance_public_ip" {
  description = "Cole este IP no navegador com a porta 8501 para ver seu app"
  value       = aws_instance.app_server.public_ip
}

output "git_repository_url" {
  description = "Link do repositorio no GitHub"
  value       = "https://github.com/seu-usuario/agente-reuniao"
}