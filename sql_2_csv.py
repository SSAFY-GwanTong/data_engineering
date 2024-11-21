import pymysql
import pandas as pd
# MySQL 연결
connection = pymysql.connect(
    host="127.0.0.1",
    user="ssafy",
    password="ssafy",
    database="ssafytrip"
)

# 테이블 목록
tables = ["sidos", "guguns", "contenttypes", "attractions"]

try:
    for table in tables:
        # SQL 실행
        query = f"SELECT * FROM {table}"
        df = pd.read_sql(query, connection)
        
        # CSV로 저장
        csv_file = f"{table}.csv"
        df.to_csv(csv_file, index=False, encoding="utf-8-sig")
        print(f"테이블 '{table}'이(가) {csv_file}로 저장되었습니다.")
finally:
    # MySQL 연결 종료
    connection.close()