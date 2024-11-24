# import pandas as pd

# # CSV 파일 경로
# after_mission_path = "./process_mission/output/after_attraction_mission.csv"
# attractions_path = "./csv/attractions.csv"

# # CSV 파일 읽기
# after_attraction_mission = pd.read_csv(after_mission_path)
# attractions = pd.read_csv(attractions_path)

# # `attraction_id`와 `content_id`가 일치하는 데이터 필터링
# filtered_attractions = attractions[attractions["content_id"].isin(after_attraction_mission["attraction_id"])]

# # 결과 출력
# print(filtered_attractions)

from openai import OpenAI
with open("./files/key2",'r') as f:
    openkey=f.read()
client = OpenAI(
    api_key=openkey
)

# Upload a file with an "assistants" purpose
file = client.files.create(
  file=open("./csv/sidos.csv", "rb"),
  purpose='assistants'
)

# Add the file to the assistant
assistant = client.beta.assistants.create(
#   instructions="You are a customer support chatbot. Use your knowledge base to best respond to customer queries.",
  model="gpt-4-1106-preview",
  tools=[{"type": "code_interpreter"}],
  tool_resources={ "code_interpreter": {"file_ids": [file.id]}} 
)

# 쓰레드 생성 및 메세지 전달
thread = client.beta.threads.create()
message = client.beta.threads.messages.create(
    thread_id = thread.id,
    role = "user",
    content = "서울의 키값은 무엇입니가?"
)
run = client.beta.threads.runs.create(
    thread_id = thread.id,
    assistant_id= assistant.id
)

# GPT 응답 대기 및 출력
import time

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