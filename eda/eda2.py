import pandas as pd
import math
import random
from tqdm import tqdm
import matplotlib.pyplot as plt

# Haversine 공식 함수 정의
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # 지구 반지름 (킬로미터)
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# CSV 파일 읽기
attractions_df = pd.read_csv("csv/attractions.csv")

# 시도 코드별로 데이터 분리
sido_groups = attractions_df.groupby("area_code")  # 'area_code'가 시도 코드 컬럼이라고 가정

# 결과 저장 리스트
min_distances = []

# 시도 코드별 처리
for sido_code, group in tqdm(sido_groups, desc="Processing by Sido Code"):
    group = group.reset_index()  # 인덱스 초기화

    # 랜덤 샘플링: 1000개 초과 시 랜덤으로 1000개 선택
    if len(group) > 1000:
        group = group.sample(n=1000, random_state=42).reset_index(drop=True)

    n = len(group)

    # 방문 여부 리스트 초기화
    visited = [False] * n

    # 시도 내에서 가장 가까운 거리 탐색
    for i in tqdm(range(n)):
        if visited[i]:  # 이미 방문한 어트랙션이면 건너뜀
            continue

        lat1, lon1 = group.loc[i, "latitude"], group.loc[i, "longitude"]
        min_distance = float("inf")
        closest_idx = -1

        # 방문하지 않은 어트랙션만 탐색
        for j in range(n):
            if i != j and not visited[j]:  # 자신이 아니고 방문하지 않은 경우
                lat2, lon2 = group.loc[j, "latitude"], group.loc[j, "longitude"]
                distance = haversine(lat1, lon1, lat2, lon2)
                if distance < min_distance:
                    min_distance = distance
                    closest_idx = j

        # 가장 가까운 어트랙션을 방문 처리
        if closest_idx != -1:
            visited[i] = True
            visited[closest_idx] = True
            min_distances.append(min_distance)

min_distances = [i for i in min_distances if i<10]

# 결과 히스토그램 생성
plt.figure(figsize=(10, 6))
plt.hist(min_distances, bins=30, color='blue', alpha=0.7, edgecolor='black')
plt.title("Histogram of Minimum Distances Between Attractions (By Sido with Sampling)")
plt.xlabel("Distance (km)")
plt.ylabel("Frequency")
plt.grid(axis='y', linestyle='--', alpha=0.7)

# 히스토그램 저장
output_path = "sido_sampled_min_distance_histogram.png"
plt.savefig(output_path, dpi=300, bbox_inches="tight")
print(f"히스토그램이 저장되었습니다: {output_path}")
