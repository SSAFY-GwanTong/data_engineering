import pandas as pd

# CSV 파일 경로

file_path = "csv/attractions.csv"

# CSV 파일 읽기
df = pd.read_csv(file_path)

# 시도(sido_code)를 기준으로 카운트
sido_counts = df['area_code'].value_counts().reset_index()
sido_counts.columns = ['sido_code', 'count']

# 결과 출력
print(sido_counts)
