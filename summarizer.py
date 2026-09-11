import os
import ollama

# Detecta se há uma URL customizada do Ollama (usada pelo Docker), senão usa o padrão local
ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
client = ollama.Client(host=ollama_host)

def generate_meeting_summary(transcript, model_name="llama3"):
    """Envia a transcrição para o Ollama gerar a ata estruturada."""
    prompt = f"""
    Analise a transcrição de reunião abaixo e forneça uma ata profissional estruturada em Markdown contendo:
    1. **Resumo Executivo**: Principais tópicos discutidos.
    2. **Decisões Tomadas**: O que foi definido ou acordado.
    3. **Tarefas Pendentes (Action Items)**: Ações práticas com responsáveis e prazos (se citados).

    Transcrição da Reunião:
    {transcript}
    """
    
    try:
        response = client.chat(model=model_name, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        return response['message']['content']
    except Exception as e:
        return f"Erro ao comunicar com o Ollama em ({ollama_host}). Certifique-se de que ele está rodando. Detalhes: {e}"