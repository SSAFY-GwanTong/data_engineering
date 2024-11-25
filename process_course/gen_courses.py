import pandas as pd
from openai import OpenAI
import os
import time
# OpenAI API 설정
with open("./files/key", 'r') as f:
    openkey = f.read().strip()
client = OpenAI(api_key=openkey)

# 시스템 프롬프트 로드
with open("./files/system_prompt2", 'r', encoding='utf-8') as f:
    system_prompt = f.read()


with open("./process_course/csv/1_attraction.csv",'r',encoding='utf-8') as f:
    data=f.read()

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": system_prompt 
        },
        {
            "role": "user",
            "content": f"{attraction_name}에서 수행할 수 있는 미션을 알려줘",
        }
    ],
    model="gpt-4o-mini",
)