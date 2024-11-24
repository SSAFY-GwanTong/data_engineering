import pandas as pd

# Fitness Type 매핑
fitness_mapping = {
    "근력": 1,
    "근지구력": 2,
    "유연성": 3,
    "심폐지구력": 4,
    "민첩성": 5,
    "순발력": 6,
    "평형성": 7,
}

# CSV 파일 읽기
df = pd.read_csv("process_course/csv/after_attraction_mission.csv")

# SQL 파일로 저장
with open("insert_after_attraction_mission.sql", "w", encoding="utf-8") as sql_file:
    for _, row in df.iterrows():
        attraction_id = row["attraction_id"]
        mission = row["mission"].replace("'", "''")  # SQL Injection 방지
        level = row["level"]

        # 1. mission INSERT 생성
        sql_file.write(f"INSERT INTO mission (attraction_id, title, level) VALUES ({attraction_id}, '{mission}', {level});\n")
        sql_file.write("SET @mission_id = LAST_INSERT_ID();\n")
        
        # 2. mission_attribute INSERT 생성
        for fitness_type, fitness_type_id in fitness_mapping.items():
            if row[fitness_type] > 0:  # fitness 값이 1 이상인 경우만 INSERT
                sql_file.write(f"INSERT INTO mission_attribute (mission_id, fitness_type_id) VALUES (@mission_id, {fitness_type_id});\n")
