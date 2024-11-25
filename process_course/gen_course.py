import pandas as pd
from openai import OpenAI
import os
import time

# 현재 실행 중인 파일의 경로
current_file_path = os.path.abspath(__file__)

# 파일이 위치한 디렉토리를 루트로 저장
ROOT_DIR = os.path.dirname(current_file_path)


# CSV 파일 경로
after_mission_path = "./process_mission/output/after_attraction_mission.csv"
attractions_path = "./csv/attractions.csv"

# CSV 파일 읽기
after_attraction_mission = pd.read_csv(after_mission_path)
attractions = pd.read_csv(attractions_path)

# `attraction_id`와 `content_id`가 일치하는 데이터 필터링
filtered_attractions = attractions[attractions["content_id"].isin(after_attraction_mission["attraction_id"])]


filtered_attractions = filtered_attractions[['content_id', 'title', 'content_type_id', 'area_code',
       'latitude', 'longitude', 'addr1', 'addr2']]


if not os.path.exists(f'{ROOT_DIR}/csv'):
    os.makedirs(f'{ROOT_DIR}/csv')
areas=set(filtered_attractions.area_code)
for i in areas:
    df1 = filtered_attractions[filtered_attractions['area_code']==i]
    if len(df1)>300:
        df1.to_csv(f'{ROOT_DIR}/csv/{i}_attraction.csv')



with open("./files/key2",'r') as f:
    openkey=f.read()
client = OpenAI(
    api_key=openkey
)

# Upload a file with an "assistants" purpose
file = client.files.create(
  file=open(f"{ROOT_DIR}/csv/1_attraction.csv", "rb"),
  purpose='assistants'
)

# 쓰레드 생성 및 메세지 전달
thread = client.beta.threads.create()

# 시스템 프롬프트 로드
with open("./files/system_prompt2", 'r', encoding='utf-8') as f:
    system_prompt = f.read()

# Add the file to the assistant
assistant = client.beta.assistants.create(
#   instructions=system_prompt,
  model="gpt-4-1106-preview",
  tools=[{"type": "code_interpreter"}],
  tool_resources={ "code_interpreter": {"file_ids": [file.id]}} 
)

# 사용자 메시지 설정
user_message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=system_prompt
)

# 실행 요청
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id
)

# GPT 응답 대기 및 출력

while True:
# Retrieve the run status
    run_status = client.beta.threads.runs.retrieve(thread_id=thread.id,run_id=run.id)
    print('try')
    time.sleep(1)
    if run_status.status == 'completed':
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        break
    else:
        ### sleep again
        time.sleep(2)

for message in reversed(messages.data):
  print(message.role + ":" + message.content[0].text.value)

# 비용 이슈가 있기 때문에 사용후 반드시 파일 제거
print(client.beta.assistants.delete(assistant_id=assistant.id))