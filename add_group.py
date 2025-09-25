import os
import django
import pandas as pd
import mysql.connector

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'club_main.settings')
django.setup()

cnx = mysql.connector.connect(
    host='localhost',
    port='3306',
    user='root',
    password='abcdefg',
    database='selection_users',
    charset='utf8mb4',
    collation='utf8mb4_general_ci'
)

data_dir = 'data'
file_list = [f for f in os.listdir(data_dir) if f.endswith('.csv')]

group_id = 6

for file in file_list:
    path = os.path.join(data_dir, file)
    csv_file = pd.read_csv(path, encoding='utf-8')

    emails = csv_file['电子邮件地址']
    uname_list = [e.split('@')[0] if pd.notna(e) else '' for e in emails]

    for uname in uname_list:
        if uname in ['dengchenluo', 'zhongyi', 'xiaoziyao', '']:
            continue

        cursor = cnx.cursor()
        cursor.execute("SELECT id FROM club_studentclubdata WHERE username=%s;", (uname,))
        result = cursor.fetchone()
        if result:
            student_id = result[0]
            cursor.execute(
                "INSERT INTO club_studentclubdata_groups (studentclubdata_id, group_id) VALUES (%s, %s);",
                (student_id, group_id)
            )
        cursor.close()

cnx.commit()
cnx.close()
