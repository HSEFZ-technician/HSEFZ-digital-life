# -*- coding: utf-8 -*-
import os
import django
import pandas as pd
import mysql.connector

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'club_main.settings')
django.setup()

# 数据库连接
cnx = mysql.connector.connect(
    host='localhost',
    port='3306',
    user='root',
    password='q1w2e3E!',   # 改成你的密码
    database='selection_users',
    charset='utf8mb4',
    collation='utf8mb4_general_ci'
)

data_dir = 'data'
# file_list = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
file_list = [f for f in os.listdir(data_dir) if f.endswith('.csv') and 'locked' in f]

for file in file_list:
    path = os.path.join(data_dir, file)
    # 假设 CSV 有两列：club_name, student_real_name
    csv_file = pd.read_csv(path, encoding='utf-8')

    club_names = csv_file['club_name']
    student_names = csv_file['student_real_name']

    for i in range(len(csv_file)):
        club_name = str(club_names[i]).strip()
        student_name = str(student_names[i]).strip()

        cursor = cnx.cursor()

        # 找到 club_eventclassinformation.id
        cursor.execute(
            "SELECT id FROM club_eventclassinformation WHERE name = %s",
            (club_name,)
        )
        club = cursor.fetchone()
        if not club:
            print(f"❌ 未找到社团: {club_name}")
            cursor.close()
            continue
        club_id = club[0]

        # 找到 club_studentclubdata.id
        cursor.execute(
            "SELECT id FROM club_studentclubdata WHERE student_real_name = %s",
            (student_name,)
        )
        stu = cursor.fetchone()
        if not stu:
            print(f"❌ 未找到学生: {student_name}")
            cursor.close()
            continue
        student_id = stu[0]

        # 插入数据（locked=1）
        cursor.execute(
            """INSERT INTO club_studentselectioninformation
               (locked, info_id_id, user_id_id)
               VALUES (1, %s, %s)""",
            (club_id, student_id)
        )
        cnx.commit()
        cursor.close()
        print(f"✅ 已加入: {club_name} - {student_name}")

cnx.close()
