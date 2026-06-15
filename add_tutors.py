# -*- coding: utf-8 -*-
import pandas as pd
import mysql.connector

# 读取你的表格 (CSV)
df = pd.read_csv("导师.csv")   # 如果是 Excel 就用 pd.read_excel("projects.xlsx")

# 数据库连接
cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="selection_users",
    charset="utf8mb4",
    collation="utf8mb4_general_ci"
)
cursor = cnx.cursor()

for idx, row in df.iterrows():
    name = str(row["name"])
    max_num = int(row["max_num"])

    desc = ""        # 简介为空
    current_num = 0
    full_desc = ""   # 详细描述为空
    hf_desc = 0
    forbid_chs = 0

    # ⚠️ 这三个外键要根据实际情况填对
    user_id_id = 1
    class_type_id = 1
    event_id_id = 1

    sql = """
    INSERT INTO club_eventclassinformation
    (name, `desc`, max_num, current_num, full_desc, hf_desc, forbid_chs, user_id_id, class_type_id, event_id_id)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    values = (name, desc, max_num, current_num, full_desc, hf_desc, forbid_chs,
              user_id_id, class_type_id, event_id_id)

    cursor.execute(sql, values)

cnx.commit()
cursor.close()
cnx.close()

print(f"成功插入 {len(df)} 条机选项目！")
