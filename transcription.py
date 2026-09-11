from faster_whisper import WhisperModel
import streamlit as st

@st.cache_resource
def load_whisper_model(model_size="base"):
    """Carrega e cacheia o modelo Whisper para otimizar a performance."""
    return WhisperModel(model_size, device="cpu", compute_type="int8")

def transcrib_file(file_path):
    """Transcreve um arquivo de áudio ou vídeo estático."""
    model = load_whisper_model()
    segments, _ = model.transcribe(file_path, beam_size=5)
    
    transcript = ""
    for segment in segments:
        transcript += f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}\n"
    return transcript

def transcribe_audio_chunk(audio_np):
    """Transcreve um bloco numpy de áudio em tempo real."""
    model = load_whisper_model()
    segments, _ = model.transcribe(audio_np, beam_size=1)
    text = ""
    for segment in segments:
        text += f" {segment.text}"
    return text