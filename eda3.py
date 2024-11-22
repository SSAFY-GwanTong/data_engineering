import pandas as pd

# CSV 파일 읽기
attractions_df = pd.read_csv("csv/attractions.csv")

# 시도별 content_type_id 개수 세기
content_count_by_sido = attractions_df.groupby(["area_code", "content_type_id"]).size().reset_index(name="count")

# 결과 출력
pd.set_option("display.max_rows", None)  # 모든 행 출력
pd.set_option("display.max_columns", None)  # 모든 열 출력
pd.set_option("display.expand_frame_repr", False)  # 줄바꿈 없이 출력
print(content_count_by_sido)


