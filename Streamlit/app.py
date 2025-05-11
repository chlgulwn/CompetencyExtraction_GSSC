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
from PromptEngine.extracting_profile import extract_competency_profile
from PromptEngine.resume_analyzer import analyze_resume
from utils.utils_file import load_transcript, save_profile_to_csv

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
        page_title="Competency Extraction System",
        page_icon="🎤",
        layout="wide"
    )

    st.title("We want to know you better...🙋🏻")
    st.markdown("""
    The system analyzes the audio of an interview with a senior or a resume to extract key competencies.
    """)

    if 'transcriber' not in st.session_state:
        st.session_state.transcriber = None
    if 'transcript' not in st.session_state:
        st.session_state.transcript = ""
    if 'is_recording' not in st.session_state:
        st.session_state.is_recording = False

    col1, col2 = st.columns(2)

    with col1:
        st.header("1. Choose an input method")
        mode = st.radio("Select an input mode ", ["Upload an audio file ", "Upload a resume"], horizontal=True)

        if mode == "Upload an audio file":
            uploaded_file = st.file_uploader("Upload an audio file", type=config['supported_audio_formats'])
            if uploaded_file is not None:
                tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1])
                tmp_file.write(uploaded_file.getvalue())
                tmp_file.flush()
                tmp_file.close()  
                audio_path = tmp_file.name  


                st.success(f"File upload completed: {uploaded_file.name}")

                if st.button("Start speech recognition "):
                    with st.spinner("Converting speech to text ..."):
                        try:
                            transcript_name = f"transcript_{uploaded_file.name.split('.')[0]}.txt"
                            transcript_text = transcribe_and_save(audio_path, save_name=transcript_name, model_size=config['whisper_model'])
                            st.session_state.transcript = transcript_text
                            st.success("Speech recognition is now complete!")
                        except Exception as e:
                            st.error(f"An error occurred during speech recognition: {str(e)}")

                os.unlink(audio_path)

        else:  
            uploaded_resume = st.file_uploader("Upload your resume file", type=config['supported_resume_formats'])
            if uploaded_resume is not None:
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_resume.name)[1]) as tmp_file:
                    tmp_file.write(uploaded_resume.getvalue())
                    resume_path = tmp_file.name

                st.success(f"Your resume is uploaded: {uploaded_resume.name}")

                if st.button("Start analyzing your resume"):
                    with st.spinner("Analyzing your resume..."):
                        try:
                            with open(resume_path, 'r', encoding='utf-8') as f:
                                resume_text = f.read()
                            profile = analyze_resume(resume_text)
                            st.session_state.transcript = profile
                            st.success("Resume analysis is complete!")
                        except Exception as e:
                            st.error(f"An error occurred during resume analysis: {str(e)}")

                os.unlink(resume_path)

    with col2:
        st.header("2. Extracting competencies")
        if st.session_state.transcript:
            if st.button("Start extracting competencies"):
                with st.spinner("Analyzing competencies..."):
                    try:
                        profile = extract_competency_profile(st.session_state.transcript)
                        st.subheader("Extracted competencies")
                        st.text_area("", profile, height=400)
                        save_profile_to_csv(profile, config['default_csv_path'])
                        st.success("Competency extraction is complete!")
                    except Exception as e:
                        st.error(f"An error occurred while extracting competencies: {str(e)}")
        else:
            st.info("Prepare your input data.")

if __name__ == "__main__":
    main()