import os
import pandas as pd

def load_transcript(file_path):
    """텍스트 파일 불러오기"""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def save_profile_to_csv(profile_data, csv_path):
    """
    역량 추출 결과를 CSV로 저장
    - profile_data: str (ex. "특기: 요리\n장점: 성실함\n...")
    - csv_path: 저장할 CSV 경로
    """
    profile_dict = {}
    for line in profile_data.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            profile_dict[key.strip()] = value.strip()

    df = pd.DataFrame([profile_dict])

    # 파일이 존재하면 이어쓰기, 없으면 새로 만들기
    if os.path.exists(csv_path):
        df.to_csv(csv_path, mode='a', header=False, index=False, encoding='utf-8-sig')
    else:
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')

    print(f"CSV 저장 완료: {csv_path}")
