import whisper
import os

# 저장할 폴더 경로
TRANSCRIPT_DIR = "interview_data/transcripts"

# 폴더가 없으면 생성
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

def transcribe_and_save(audio_path, save_name="transcript1.txt"):
    # Whisper 모델 로드
    model = whisper.load_model("base")

    # 음성 파일 → 텍스트 추출
    result = model.transcribe(audio_path)
    transcript_text = result["text"]

    # 파일 저장 경로
    save_path = os.path.join(TRANSCRIPT_DIR, save_name)

    # 텍스트 파일로 저장
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(transcript_text)

    print(f"텍스트 저장 완료: {save_path}")
    return transcript_text

if __name__ == "__main__":
    # 테스트용 음성 파일
    audio_path = "sample_audio.wav"  # 음성 파일 넣을 예정
    transcribe_and_save(audio_path, save_name="interview_senior1.txt")
