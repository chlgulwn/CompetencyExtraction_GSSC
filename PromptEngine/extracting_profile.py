import openai
import os
from dotenv import load_dotenv
from PromptEngine.prompt_template import build_prompt

# API Key 로딩
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_competency_profile(user_text):
    prompt = build_prompt(user_text)

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
    )

    result = response['choices'][0]['message']['content'].strip()
    return result

if __name__ == "__main__":
    # 예시 실행
    sample_text = "안녕하세요. 저는 20년간 뷰티 업계에서 마케팅과 제품 개발을 했고, 최근에는 1인 창업을 준비하고 있어요. 협업도 잘 하고요!"
    print(extract_competency_profile(sample_text))
