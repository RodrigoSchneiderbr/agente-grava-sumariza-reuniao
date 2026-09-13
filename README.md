# 🎙️ Agente de IA Open Source para Transcrição e Resumo de Reuniões

Um agente de inteligência artificial 100% local, open-source e focado em **privacidade** para transcrever áudios de reuniões e gerar atas inteligentes estruturadas (resumo executivo, decisões e tarefas pendentes). 

Nenhum dado ou áudio sai do seu computador — tudo roda localmente utilizando o seu próprio hardware.

---

## 🚀 Tecnologias Utilizadas

* **[Streamlit](https://streamlit.io/)**: Interface gráfica web interativa e elegante.
* **[Faster-Whisper](https://github.com/SYSTRAN/faster-whisper)**: Transcrição de áudio de altíssima velocidade e precisão baseada no modelo Whisper da OpenAI.
* **[Ollama](https://ollama.com/)**: Execução local de Modelos de Linguagem Grandes (LLMs) como *Llama 3/3.1* ou *Qwen 2.5*.
* **[SoundDevice](https://python-sounddevice.readthedocs.io/) & NumPy**: Captura de áudio ao vivo do microfone em tempo real.
* **FPDF2 & python-docx**: Exportação automática dos resultados para **PDF** e **Word (.docx)**.

---

## 📁 Estrutura do Projeto

```text
agente-reuniao/
│
├── app.py               # Interface gráfica principal (Streamlit)
├── transcription.py     # Lógica de transcrição (Faster-Whisper)
├── summarizer.py        # Integração com o Ollama para geração de atas
├── exporter.py          # Módulo de exportação para PDF e Word (.docx)
├── requirements.txt     # Lista de dependências Python
├── terraform/           # Arquivos de infraestrutura como código (IaC)
│   ├── providers.tf     # Configuração da AWS
│   ├── variables.tf     # Variáveis do Terraform
│   ├── network.tf       # VPC e Security Groups
│   ├── ec2.tf           # Configuração da Instância EC2
│   └── outputs.tf       # IPs e links de saída
├── .gitignore           # Arquivos ignorados pelo controle de versão
└── README.md            # Documentação do projeto
```

## ⚙️ Pré-requisitos
Python 3.10 ou superior instalado.

Ollama instalado e rodando na sua máquina. Baixe em ollama.com

```text
ollama pull llama3.1
```

## 📦 Instalação e Configuração
Clone ou baixe este repositório para o seu computador e abra o terminal na pasta raiz do projeto, no Windows

Crie e ative um ambiente virtual (venv):

```text
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
Instalar dependencias
```text
pip install -r requirements.txt
```

## 🖥️ Como Executar a Aplicação
Com o ambiente virtual ativo e o Ollama rodando no seu sistema, execute o comando do Streamlit:

```text
streamlit run app.py
```

💡 Modos de Operação
📁 Upload de Arquivo:

Envie um arquivo de áudio gravado (.mp3, .wav ou .m4a).
O sistema transcreve o arquivo e gera a ata inteligente automaticamente.
Opção para baixar os resultados em PDF ou Word.

🔴 Gravação ao Vivo:

Inicie a gravação direto pelo microfone da sua máquina.
Acompanhe o texto sendo transcrito progressivamente na tela em blocos de tempo real.
Ao finalizar, gere a ata consolidada e exporte o documento.

## 🐳 Como Executar via Docker (Opcional - Ideal para Upload de Mídia)
Nota: O modo de gravação ao vivo via microfone físico não é suportado nativamente dentro de containers no Windows/Mac, mas o upload de arquivos funciona perfeitamente.

Certifique-se de que o Ollama está rodando na sua máquina.

Na raiz do projeto, execute o Docker Compose:
```text
docker compose up --build
```
Acesse no navegador: http://localhost:8501

## Deploy na AWS com Terraform (EC2)
Para subir a aplicação para a nuvem de forma automatizada utilizando uma instância EC2 da AWS, siga os passos abaixo:

1. Provisionar a Infraestrutura com o Terraform
Certifique-se de ter o Terraform instalado e as suas credenciais da AWS configuradas (aws configure).

2. Entre na pasta do Terraform:

```text
cd terraform
```
3. Inicialize e aplique a infraestrutura:

```text
terraform init
terraform plan
terraform apply
```
4. O Terraform exibirá no final o IP Público da sua instância EC2.

## Configurar a Aplicação na Nuvem

1. Conecte-se na sua instância EC2 via SSH ou acesse-a, e clone o seu repositório:

```text
git clone https://github.com/RodrigoSchneiderbr/agente-grava-sumariza-reuniao
cd agente-reuniao
```
2. Suba a aplicação utilizando o Docker diretamente na máquina (o script do Terraform já instala o Docker automaticamente):

```text
docker build -t agente-reuniao .
docker run -d -p 8501:8501 --restart always agente-reuniao
```

📄 Licença
Este projeto é de código aberto sob a licença MIT. Sinta-se à vontade para modificar e melhorar!