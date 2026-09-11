import ollama

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
        response = ollama.chat(model=model_name, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        return response['message']['content']
    except Exception as e:
        return f"Erro ao comunicar com o Ollama. Certifique-se de que ele está rodando localmente. Detalhes: {e}"