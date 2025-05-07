import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
import logging
from pathlib import Path
from typing import Optional
import yaml
import tempfile
from STT_whisper.transcribe import transcribe_and_save
from STT_whisper.realtime_transcribe import RealtimeTranscriber
from PromptEngine.extracting_profile import extract_competency_profile
from PromptEngine.resume_analyzer import analyze_resume
from utils.utils_file import load_transcript, save_profile_to_csv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_config() -> dict:
    config_path = Path("config.yaml")
    if not config_path.exists():
        raise FileNotFoundError("config.yaml file not found")
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def update_transcript(text: str):
    st.session_state.transcript += text + "\n"

def main():
    config = load_config()

    st.set_page_config(
        page_title="시니어 역량 추출 시스템",
        page_icon="🎤",
        layout="wide"
    )

    st.title("🎤 시니어 역량 추출 시스템")
    st.markdown("""
    이 시스템은 시니어와의 인터뷰 음성 또는 이력서를 분석하여 핵심 역량을 추출합니다.
    """)

    if 'transcriber' not in st.session_state:
        st.session_state.transcriber = None
    if 'transcript' not in st.session_state:
        st.session_state.transcript = ""
    if 'is_recording' not in st.session_state:
        st.session_state.is_recording = False

    col1, col2 = st.columns(2)

    with col1:
        st.header("1. 입력 방식 선택")
        mode = st.radio("입력 모드 선택", ["실시간 음성 인식", "음성 파일 업로드", "이력서 업로드"], horizontal=True)

        if mode == "실시간 음성 인식":
            if st.button("🎤 녹음 시작", disabled=st.session_state.is_recording):
                try:
                    st.session_state.transcriber = RealtimeTranscriber(
                        model_size=config['whisper_model'],
                        callback=update_transcript  
                    )
                    st.session_state.transcriber.start_recording()
                    st.session_state.is_recording = True
                    st.success("녹음이 시작되었습니다. 말씀해주세요...")
                except Exception as e:
                    st.error(f"녹음 시작 중 오류가 발생했습니다: {str(e)}")

            if st.button("⏹️ 녹음 중지", disabled=not st.session_state.is_recording):
                try:
                    st.session_state.transcriber.stop_recording()
                    st.session_state.is_recording = False
                    st.success("녹음이 중지되었습니다.")
                except Exception as e:
                    st.error(f"녹음 중지 중 오류가 발생했습니다: {str(e)}")

            st.subheader("인식된 텍스트")
            st.text_area("", st.session_state.transcript, height=200, key="transcript_area")

        elif mode == "음성 파일 업로드":
            uploaded_file = st.file_uploader("인터뷰 음성 파일을 업로드하세요", type=config['supported_audio_formats'])
            if uploaded_file is not None:
                tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1])
                tmp_file.write(uploaded_file.getvalue())
                tmp_file.flush()
                tmp_file.close()  
                audio_path = tmp_file.name  


                st.success(f"파일 업로드 완료: {uploaded_file.name}")

                if st.button("음성 인식 시작"):
                    with st.spinner("음성을 텍스트로 변환 중..."):
                        try:
                            transcript_name = f"transcript_{uploaded_file.name.split('.')[0]}.txt"
                            transcript_text = transcribe_and_save(audio_path, save_name=transcript_name, model_size=config['whisper_model'])
                            st.session_state.transcript = transcript_text
                            st.success("음성 인식이 완료되었습니다!")
                        except Exception as e:
                            st.error(f"음성 인식 중 오류가 발생했습니다: {str(e)}")

                os.unlink(audio_path)

        else:  
            uploaded_resume = st.file_uploader("이력서 파일을 업로드하세요", type=config['supported_resume_formats'])
            if uploaded_resume is not None:
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_resume.name)[1]) as tmp_file:
                    tmp_file.write(uploaded_resume.getvalue())
                    resume_path = tmp_file.name

                st.success(f"이력서 업로드 완료: {uploaded_resume.name}")

                if st.button("이력서 분석 시작"):
                    with st.spinner("이력서를 분석 중..."):
                        try:
                            with open(resume_path, 'r', encoding='utf-8') as f:
                                resume_text = f.read()
                            profile = analyze_resume(resume_text)
                            st.session_state.transcript = profile
                            st.success("이력서 분석이 완료되었습니다!")
                        except Exception as e:
                            st.error(f"이력서 분석 중 오류가 발생했습니다: {str(e)}")

                os.unlink(resume_path)

    with col2:
        st.header("2. 역량 추출")
        if st.session_state.transcript:
            if st.button("역량 추출 시작"):
                with st.spinner("역량을 분석 중..."):
                    try:
                        profile = extract_competency_profile(st.session_state.transcript)
                        st.subheader("추출된 역량")
                        st.text_area("", profile, height=400)
                        save_profile_to_csv(profile, config['default_csv_path'])
                        st.success("역량 추출이 완료되었습니다!")
                    except Exception as e:
                        st.error(f"역량 추출 중 오류가 발생했습니다: {str(e)}")
        else:
            st.info("입력 데이터를 먼저 준비해주세요.")

if __name__ == "__main__":
    main()