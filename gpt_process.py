import pandas as pd
from openai import OpenAI
import json
import os
from tqdm import tqdm  # tqdm 추가

# 입력 및 출력 파일 경로
attractions_path = "./csv/attractions.csv"
output_path = "./output/filtered_attractions.csv"
progress_file = "./progress.json"
error_file = "./error_state.json"
results_file = "./missions.csv"

# 샘플링 개수 (사용자가 원하는 개수로 변경 가능)
SAMPLE_SIZE = 50  # 그룹당 최대 샘플링 개수

# JSON 파일 로드 함수
def load_json(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# JSON 파일 저장 함수
def save_json(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# 전처리 작업
if not os.path.exists(output_path):
    # CSV 파일 읽기
    attractions_df = pd.read_csv(attractions_path, encoding="utf-8")

    # area_code와 content_type_id 별로 개수 세기
    grouped = attractions_df.groupby(["area_code", "content_type_id"]).size().reset_index(name="count")

    # 100개 이상인 그룹 필터링
    large_groups = grouped[grouped["count"] > SAMPLE_SIZE]

    # 랜덤 샘플링 결과를 저장할 데이터프레임
    sampled_df = pd.DataFrame()

    # 각 그룹에서 SAMPLE_SIZE개씩 샘플링
    for _, row in large_groups.iterrows():
        area_code = row["area_code"]
        content_type_id = row["content_type_id"]

        # 해당 그룹의 데이터 가져오기
        group_data = attractions_df[
            (attractions_df["area_code"] == area_code) & 
            (attractions_df["content_type_id"] == content_type_id)
        ]

        # 랜덤 샘플링 (SAMPLE_SIZE 개수)
        sampled_group = group_data.sample(n=SAMPLE_SIZE, random_state=42)  # 랜덤 시드 고정
        sampled_df = pd.concat([sampled_df, sampled_group], ignore_index=True)

    # SAMPLE_SIZE 이하인 그룹 추가 (전체 포함)
    small_groups = grouped[grouped["count"] <= SAMPLE_SIZE]
    for _, row in small_groups.iterrows():
        area_code = row["area_code"]
        content_type_id = row["content_type_id"]

        # 해당 그룹의 데이터 가져오기
        group_data = attractions_df[
            (attractions_df["area_code"] == area_code) & 
            (attractions_df["content_type_id"] == content_type_id)
        ]
        sampled_df = pd.concat([sampled_df, group_data], ignore_index=True)

    # 전처리 결과 저장
    os.makedirs("./output", exist_ok=True)  # 디렉토리 생성
    sampled_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"Filtered data saved to {output_path}")
else:
    print(f"Filtered data already exists at {output_path}")

# 전처리된 파일 읽기
filtered_attractions = pd.read_csv(output_path, encoding="utf-8")

# 진행 상태 및 에러 상태 로드
progress = load_json(progress_file)
error_state = load_json(error_file)

# 작업 시작 인덱스 (에러 발생 시 저장된 인덱스부터 시작)
start_idx = error_state.get("last_index", 0)

# OpenAI API 키 설정
with open("./files/key", 'r') as f:
    openkey = f.read().strip()
client = OpenAI(api_key=openkey)

# 시스템 프롬프트 로드
with open("./files/system_prompt", 'r', encoding='utf-8') as f:  # UTF-8로 인코딩 설정
    system_prompt = f.read()

# 결과 저장용 리스트 초기화
results = []

# 기존 결과 파일이 존재하면 불러오기
if os.path.exists(results_file):
    results = pd.read_csv(results_file).to_dict(orient="records")

# tqdm 추가: 필터링된 어트랙션 순회 처리
for idx, row in tqdm(filtered_attractions.iloc[start_idx:].iterrows(), total=len(filtered_attractions.iloc[start_idx:]), desc="Processing Attractions"):
    attraction_id = row["no"]  # 어트랙션 번호
    attraction_name = row["title"]  # 어트랙션 이름

    # 이미 처리된 어트랙션은 건너뛰기
    if str(attraction_id) in progress:
        continue

    try:
        # OpenAI API 호출
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

        # 응답 파싱
        response = chat_completion.choices[0].message.content.strip()
        missions = eval(response)  # 응답 문자열을 Python 리스트로 변환

        # 각 미션을 처리하여 결과 저장
        for mission, tags in missions:
            tag_columns = {tag: 1 for tag in ["근력", "근지구력", "유연성", "심폐지구력", "민첩성", "순발력", "평형성"]}
            tag_columns.update({tag: 0 for tag in tag_columns if tag not in tags})
            results.append({"attraction_id": attraction_id, "mission": mission, **tag_columns})

        # 진행 상태 저장
        progress[str(attraction_id)] = missions
        save_json(progress_file, progress)

    except Exception as e:
        # 에러 발생 시 현재 상태 저장 및 종료
        error_state = {"last_index": idx, "error": str(e), "attraction_id": attraction_id, "response": response if 'response' in locals() else None}
        save_json(error_file, error_state)
        print(f"Error at index {idx} ({attraction_name}): {e}")
        break

# 결과 CSV 파일로 저장
results_df = pd.DataFrame(results)
results_df.to_csv(results_file, index=False, encoding="utf-8-sig")
print("Processing complete. Results saved to missions.csv.")
