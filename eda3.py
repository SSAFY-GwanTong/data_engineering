import pandas as pd

# CSV 파일 읽기
attractions_df = pd.read_csv("csv/attractions.csv")

# 시도별 content_id 개수 세기
content_count_by_sido = attractions_df.groupby(["area_code", "content_id"]).size().reset_index(name="count")

# 결과 출력
print(content_count_by_sido)


