import pandas as pd
import os

# 입력 및 출력 파일 경로
attractions_path = "./csv/attractions.csv"
output_path = "./process/output/filtered_attractions.csv"

# 샘플링 개수 (사용자가 원하는 개수로 변경 가능)
SAMPLE_SIZE = 50  # 그룹당 최대 샘플링 개수

def preprocess():
    if not os.path.exists(output_path):
        # CSV 파일 읽기
        attractions_df = pd.read_csv(attractions_path, encoding="utf-8")

        # area_code와 content_type_id 별로 개수 세기
        grouped = attractions_df.groupby(["area_code", "content_type_id"]).size().reset_index(name="count")

        # SAMPLE_SIZE개 이상인 그룹 필터링
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
        os.makedirs("./process/output", exist_ok=True)  # 디렉토리 생성
        sampled_df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"Filtered data saved to {output_path}")
    else:
        print(f"Filtered data already exists at {output_path}")

if __name__ == "__main__":
    preprocess()
