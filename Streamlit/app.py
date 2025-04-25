import streamlit as st
import os
import logging
from pathlib import Path
from typing import Optional
import yaml
import tempfile
from STT_whisper.transcribe import transcribe_and_save
from STT_whisper.realtime_transcribe import RealtimeTranscriber
from PromptEngine.extracting_profile import extract_competency_profile
from utils.utils_file import load_transcript, save_profile_to_csv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_config() -> dict:
    """Load configuration from YAML file"""
    config_path = Path("config.yaml")
    if not config_path.exists():
        raise FileNotFoundError("config.yaml file not found")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    # Load configuration
    config = load_config()
    
    # Set page configuration
    st.set_page_config(
        page_title="시니어 역량 추출 시스템",
        page_icon="🎤",
        layout="wide"
    )
    
    # Title and description
    st.title("🎤 시니어 역량 추출 시스템")
    st.markdown("""
    이 시스템은 시니어와의 인터뷰 음성을 텍스트로 변환하고, 
    대화 내용을 분석하여 핵심 역량을 추출합니다.
    """)
    
    # Initialize session state
    if 'transcriber' not in st.session_state:
        st.session_state.transcriber = None
    if 'transcript' not in st.session_state:
        st.session_state.transcript = ""
    if 'is_recording' not in st.session_state:
        st.session_state.is_recording = False
    
    # Create two columns for the main content
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("1. 음성 입력")
        
        # Mode selection
        mode = st.radio(
            "입력 모드 선택",
            ["실시간 음성 인식", "파일 업로드"],
            horizontal=True
        )
        
        if mode == "실시간 음성 인식":
            # Real-time transcription
            if st.button("🎤 녹음 시작", disabled=st.session_state.is_recording):
                try:
                    # Initialize transcriber
                    st.session_state.transcriber = RealtimeTranscriber(
                        model_size=config['whisper_model'],
                        callback=lambda text: st.session_state.transcript += text + "\n"
                    )
                    
                    # Start recording
                    st.session_state.transcriber.start_recording()
                    st.session_state.is_recording = True
                    st.success("녹음이 시작되었습니다. 말씀해주세요...")
                    
                except Exception as e:
                    st.error(f"녹음 시작 중 오류가 발생했습니다: {str(e)}")
            
            if st.button("⏹️ 녹음 중지", disabled=not st.session_state.is_recording):
                try:
                    # Stop recording
                    st.session_state.transcriber.stop_recording()
                    st.session_state.is_recording = False
                    st.success("녹음이 중지되었습니다.")
                    
                except Exception as e:
                    st.error(f"녹음 중지 중 오류가 발생했습니다: {str(e)}")
            
            # Display transcript
            st.subheader("인식된 텍스트")
            transcript_text = st.text_area(
                "",
                st.session_state.transcript,
                height=200,
                key="transcript_area"
            )
            
        else:
            # File upload
            uploaded_file = st.file_uploader(
                "인터뷰 음성 파일을 업로드하세요",
                type=config['supported_audio_formats']
            )
            
            if uploaded_file is not None:
                # Save uploaded file to temporary location
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    audio_path = tmp_file.name
                
                # Display file information
                st.success(f"파일 업로드 완료: {uploaded_file.name}")
                
                # Transcription
                if st.button("음성 인식 시작"):
                    with st.spinner("음성을 텍스트로 변환 중..."):
                        try:
                            # Generate unique filename
                            transcript_name = f"transcript_{uploaded_file.name.split('.')[0]}.txt"
                            
                            # Transcribe audio
                            transcript_text = transcribe_and_save(
                                audio_path,
                                save_name=transcript_name,
                                model_size=config['whisper_model']
                            )
                            
                            # Store transcript in session state
                            st.session_state.transcript = transcript_text
                            
                            st.success("음성 인식이 완료되었습니다!")
                            
                        except Exception as e:
                            st.error(f"음성 인식 중 오류가 발생했습니다: {str(e)}")
                
                # Clean up temporary file
                os.unlink(audio_path)
    
    with col2:
        st.header("2. 역량 추출")
        
        if st.session_state.transcript:
            if st.button("역량 추출 시작"):
                with st.spinner("역량을 분석 중..."):
                    try:
                        # Extract competency profile
                        profile = extract_competency_profile(st.session_state.transcript)
                        
                        # Display profile
                        st.subheader("추출된 역량")
                        st.text_area("", profile, height=400)
                        
                        # Save to CSV
                        save_profile_to_csv(
                            profile,
                            config['default_csv_path']
                        )
                        
                        st.success("역량 추출이 완료되었습니다!")
                        
                    except Exception as e:
                        st.error(f"역량 추출 중 오류가 발생했습니다: {str(e)}")
        else:
            st.info("음성 인식을 먼저 완료해주세요.")

if __name__ == "__main__":
    main()