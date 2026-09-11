import os
import queue
import threading
import time
import numpy as np
import sounddevice as sd
import streamlit as st

from summarizer import generate_meeting_summary
from transcription import transcrib_file, transcribe_audio_chunk
from exporter import create_pdf_bytes, create_docx_bytes

st.set_page_config(page_title="Agente Open Source de Reuniões", page_icon="🎙️", layout="wide")

st.title("🎙️ Agente de IA Open Source para Reuniões")
st.write("Escolha o modo de operação: Upload de Áudio/Vídeo ou Transcrição ao Vivo com Microfone.")

mode = st.sidebar.radio("Modo de Operação", ["📁 Upload de Mídia", "🔴 Gravação ao Vivo"])

def get_input_devices():
    devices = sd.query_devices()
    input_devices = []
    for idx, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            input_devices.append((idx, device['name']))
    return input_devices

# ==================== MODO 1: UPLOAD DE MÍDIA ====================
if mode == "📁 Upload de Mídia":
    st.subheader("Processamento de Arquivo de Áudio ou Vídeo")
    media_file = st.file_uploader("Envie o arquivo de áudio ou vídeo", type=["mp3", "wav", "m4a", "mp4", "mkv", "avi", "mov"])

    if media_file is not None:
        ext = media_file.name.split('.')[-1]
        temp_path = f"temp_media_file.{ext}"
        with open(temp_path, "wb") as f:
            f.write(media_file.getbuffer())
        
        if ext.lower() in ['mp4', 'mkv', 'avi', 'mov']:
            st.video(temp_path)
        else:
            st.audio(temp_path)
        
        if st.button("Processar e Gerar Ata"):
            with st.spinner("Transcrevendo mídia com Faster-Whisper..."):
                transcript = transcrib_file(temp_path)
            
            with st.spinner("Gerando resumo executivo com Ollama..."):
                summary = generate_meeting_summary(transcript)
            
            st.session_state.last_summary = summary
            st.session_state.last_transcript = transcript
            
            if os.path.exists(temp_path):
                os.remove(temp_path)

        if "last_summary" in st.session_state and "last_transcript" in st.session_state:
            tab1, tab2 = st.tabs(["📋 Ata Inteligente", "📝 Transcrição Completa"])
            with tab1:
                st.markdown(st.session_state.last_summary)
            with tab2:
                st.text_area("Texto Transcrito", st.session_state.last_transcript, height=300)
                
            st.divider()
            st.subheader("💾 Exportar Resultados")
            col_pdf, col_docx = st.columns(2)
            
            pdf_data = create_pdf_bytes("Ata de Reunião - Inteligente", st.session_state.last_summary, st.session_state.last_transcript)
            docx_data = create_docx_bytes("Ata de Reunião - Inteligente", st.session_state.last_summary, st.session_state.last_transcript)
            
            with col_pdf:
                st.download_button(label="📥 Baixar em PDF", data=pdf_data, file_name="ata_reuniao.pdf", mime="application/pdf")
            with col_docx:
                st.download_button(label="📥 Baixar em Word (.docx)", data=docx_data, file_name="ata_reuniao.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

# ==================== MODO 2: AO VIVO ====================
elif mode == "🔴 Gravação ao Vivo":
    st.subheader("Transcrição e Ata em Tempo Real")
    
    # Identifica e exibe o microfone padrão do sistema
    default_input_idx = sd.default.device[0]
    if default_input_idx >= 0 and default_input_idx < len(sd.query_devices()):
        default_mic_name = sd.query_devices(default_input_idx)['name']
        if default_mic_name.count('(') > default_mic_name.count(')'):
            default_mic_name += ')'
            st.info(f"🎤 **Microfone padrão do sistema:** {default_mic_name}")

    input_devs = get_input_devices()
    if not input_devs:
        st.error("Nenhum microfone ou dispositivo de entrada de áudio foi encontrado no seu computador.")
    else:
        dev_names = [d[1] for d in input_devs]
        dev_indices = [d[0] for d in input_devs]
        
        default_index = 0
        if default_input_idx in dev_indices:
            default_index = dev_indices.index(default_input_idx)

        selected_dev_name = st.selectbox("Selecione o Microfone para Gravação:", dev_names, index=default_index)
        selected_dev_idx = dev_indices[dev_names.index(selected_dev_name)]

    SAMPLE_RATE = 16000
    BLOCK_DURATION = 5  
    
    if "transcript_live" not in st.session_state:
        st.session_state.transcript_live = ""
    if "is_recording" not in st.session_state:
        st.session_state.is_recording = False
    if "summary_live" not in st.session_state:
        st.session_state.summary_live = ""
    if "stop_event" not in st.session_state:
        st.session_state.stop_event = threading.Event()

    audio_queue = queue.Queue()

    def audio_callback(indata, frames, time_info, status):
        if status:
            print(status)
        audio_queue.put(indata.copy())

    def record_loop(stop_signal, device_idx):
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=audio_callback, blocksize=int(SAMPLE_RATE * BLOCK_DURATION), device=device_idx):
            while not stop_signal.is_set():
                time.sleep(0.1)

    col1, col2 = st.columns(2)
    with col1:
        if not st.session_state.is_recording:
            if st.button("▶️ Iniciar Gravação ao Vivo", type="primary"):
                st.session_state.transcript_live = ""
                st.session_state.summary_live = ""
                st.session_state.is_recording = True
                st.session_state.stop_event.clear()
                
                threading.Thread(target=record_loop, args=(st.session_state.stop_event, selected_dev_idx), daemon=True).start()
                st.rerun()
        else:
            if st.button("⏹️ Parar Gravação", type="secondary"):
                st.session_state.is_recording = False
                st.session_state.stop_event.set()
                st.rerun()

    if st.session_state.is_recording:
        st.warning(f"🔴 Gravando com: **{selected_dev_name}**. Fale ao microfone...")
        placeholder = st.empty()
        
        while st.session_state.is_recording:
            try:
                audio_data = audio_queue.get(timeout=1.0)
                audio_np = np.squeeze(audio_data).astype(np.float32)
                
                chunk_text = transcribe_audio_chunk(audio_np)
                st.session_state.transcript_live += chunk_text
                
                placeholder.text_area("Transcrição em Tempo Real", st.session_state.transcript_live, height=250)
            except queue.Empty:
                continue
    else:
        if st.session_state.transcript_live:
            st.success("Gravação encerrada com sucesso!")
            st.text_area("Transcrição Final", st.session_state.transcript_live, height=250)
            
            if st.button("Gerar Ata Inteligente da Reunião ao Vivo"):
                with st.spinner("Gerando ata com Ollama..."):
                    st.session_state.summary_live = generate_meeting_summary(st.session_state.transcript_live)
            
            if st.session_state.summary_live:
                st.markdown("### Ata da Reunião")
                st.markdown(st.session_state.summary_live)
                
                st.divider()
                st.subheader("💾 Exportar Resultados da Reunião ao Vivo")
                col_pdf_live, col_docx_live = st.columns(2)
                
                pdf_data_live = create_pdf_bytes("Ata de Reunião - Ao Vivo", st.session_state.summary_live, st.session_state.transcript_live)
                docx_data_live = create_docx_bytes("Ata de Reunião - Ao Vivo", st.session_state.summary_live, st.session_state.transcript_live)
                
                with col_pdf_live:
                    st.download_button(label="📥 Baixar em PDF", data=pdf_data_live, file_name="ata_reuniao_ao_vivo.pdf", mime="application/pdf")
                with col_docx_live:
                    st.download_button(label="📥 Baixar em Word (.docx)", data=docx_data_live, file_name="ata_reuniao_ao_vivo.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")