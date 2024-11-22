import os
from openai import OpenAI
from tqdm import tqdm

# 입력 및 출력 파일 경로
filtered_attractions_path = "./process/output/filtered_attractions.csv"
missions_file = "./process/output/attraction_mission.csv"
error_log_file = "./process/output/error_log.txt"

# OpenAI API 설정
with open("./files/key", 'r') as f:
    openkey = f.read().strip()
client = OpenAI(api_key=openkey)

# 시스템 프롬프트 로드
with open("./files/system_prompt", 'r', encoding='utf-8') as f:
    system_prompt = f.read()

# 작업 초기화
start_mode = input("새로 시작하시겠습니까? (y/n): ").strip().lower()

# 시작 인덱스 설정
start_idx = 0

if start_mode == "y":
    # 새로 시작: 결과 파일 초기화
    with open(missions_file, "w", encoding="utf-8-sig") as f:
        f.write("attraction_id,mission,level,근력,근지구력,유연성,심폐지구력,민첩성,순발력,평형성\n")  # 헤더 작성
elif start_mode == "n":
    # 기존 작업 이어서: 마지막 attraction_id 확인
    if os.path.exists(missions_file):
        with open(missions_file, "r", encoding="utf-8-sig") as f:
            lines = f.readlines()
            # 파일이 비어 있는 경우
            if len(lines) <= 1:
                print("기존 파일이 비어 있습니다. 새로 작업을 시작합니다.")
            else:
                # 마지막 줄이 공백이라면 그 전 줄 확인
                last_line = lines[-1].strip()
                if not last_line:  # 공백 줄 확인
                    last_line = lines[-2].strip()

                # 마지막 줄의 attraction_id 추출
                last_attraction_id = last_line.split(",")[0]

                # "attraction_id"이면 데이터가 없는 상태
                if last_attraction_id == "attraction_id":
                    print("기존 파일에 데이터가 없습니다. 새로 작업을 시작합니다.")
                else:
                    # 전처리된 파일에서 마지막 attraction_id의 인덱스 찾기
                    with open(filtered_attractions_path, "r", encoding="utf-8") as f_filtered:
                        for idx, line in enumerate(f_filtered):
                            if line.startswith(last_attraction_id):
                                start_idx = idx + 1  # 다음 인덱스부터 작업
                                break
    else:
        print("기존 작업 파일이 없습니다. 새로 작업을 시작합니다.")
else:
    print("잘못된 입력입니다. 프로그램을 종료합니다.")
    exit()

# 전처리된 파일 읽기
with open(filtered_attractions_path, "r", encoding="utf-8") as f:
    filtered_attractions = f.readlines()

# tqdm으로 진행 상황 표시
for idx, line in tqdm(enumerate(filtered_attractions[start_idx:]), total=len(filtered_attractions[start_idx:]), desc="Processing Attractions"):
    parts = line.strip().split(",")
    attraction_id = parts[0]  # 어트랙션 번호
    attraction_name = parts[1]  # 어트랙션 이름

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

        # python``` 태그 제거
        if response.startswith("python```"):
            response = response[len("python```"):].strip()
        if response.endswith("```"):
            response = response[:-len("```")].strip()

        # 응답을 Python 리스트로 변환
        missions = eval(response)

        # 각 미션을 처리하여 CSV에 저장
        with open(missions_file, "a", encoding="utf-8-sig") as f:
            for mission, level, tags in missions:
                # 원핫인코딩
                tag_columns = {tag: 1 for tag in ["근력", "근지구력", "유연성", "심폐지구력", "민첩성", "순발력", "평형성"]}
                tag_columns.update({tag: 0 for tag in tag_columns if tag not in tags})

                # CSV 행 작성
                f.write(
                    f"{attraction_id},{mission},{level}," +
                    f"{tag_columns['근력']},{tag_columns['근지구력']},{tag_columns['유연성']}," +
                    f"{tag_columns['심폐지구력']},{tag_columns['민첩성']},{tag_columns['순발력']},{tag_columns['평형성']}\n"
                )

    except Exception as e:
        # 에러 로그 작성
        with open(error_log_file, "a", encoding="utf-8-sig") as f:
            f.write(f"Error for Attraction ID {attraction_id}: {str(e)}\n")
        print(f"Error for Attraction ID {attraction_id}: {str(e)}")
