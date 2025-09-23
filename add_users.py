# # -*- coding: utf-8 -*-
# import pandas as pd
# import os
# from club.tokens import *
# # from club.models import *
# import mysql.connector
# from django.contrib.auth.hashers import make_password

# fileList = os.listdir('data')
# # print(fileList)

# cnx = mysql.connector.connect(
#     host='localhost',
#     port='3306',
#     user='root',
#     password='123',
#     database='selection_users',
# )

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'club_main.settings')


# num = 1475

# for i in fileList:
#     path = 'data/' + i
#     class_name = i[0:i.find('.')]
#     # print(class_name)
#     csvFile = pd.read_csv(path, encoding='gb18030')
#     real_names = csvFile['名称']
#     emails = csvFile['电子邮件地址']
#     date = csvFile['修改时间']
#     uname = []
#     for j in emails:
#         atC = j.find('@')
#         substr = j[0:atC]
#         uname.append(substr)
#         # print(substr)
#     for i in range(len(emails)):
#         # scd = StudentClubData(email=emails[i], username=uname[i], student_id=class_name,
#         #                       student_real_name=real_names[i], is_created=False, is_active=False, is_staff=False, is_superuser=False)
#         # scd.set_password(PasswordGenerator(20))
#         # scd.groups.add("学生")
#         # scd.save()
#         if uname[i] == 'dengchenluo' or uname[i] == 'zhongyi' or uname[i] == 'xiaoziyao' or uname[i] == '':
#             continue
#         cursor = cnx.cursor()
#         command = "INSERT INTO club_studentclubdata (email, username, student_id, student_real_name, is_created, is_active, is_staff, is_superuser, password, date_joined) VALUES (\'%s\', \'%s\', \'%s\', \'%s\', 0,0,0,0, \'%s\', \'%s\');"
#         val = (emails[i], uname[i], class_name,
#                real_names[i], make_password(PasswordGenerator(20)), date[i])
#         num += 1
#         cursor.execute(command % val)
#         cursor.close()

# cnx.commit()

# # for i in range(num):
# #     if i <= 5:
# #         continue
# #     cursor = cnx.cursor()
# #     command = "INSERT INTO club_studentclubdata_groups (studentclubdata_id, group_id) VALUES (%d, 2);"
# #     val = (i)
# #     print(command % val)
# #     cursor.execute(command % val)
# #     cursor.close()

# cnx.commit()
# cnx.close()


import os
import django
import pandas as pd
import mysql.connector
from club.tokens import *
from django.contrib.auth.hashers import make_password
import datetime

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
num = 1475

for file in file_list:
    path = os.path.join(data_dir, file)
    csv_file = pd.read_csv(path, encoding='utf-8')

    real_names = csv_file['名称']
    emails = csv_file['电子邮件地址']
    student_ids = csv_file['学号']

    uname = [e.split('@')[0] if pd.notna(e) else '' for e in emails]

    for i in range(len(emails)):
        if uname[i] in ['dengchenluo', 'zhongyi', 'xiaoziyao', '']:
            continue

        full_id = str(student_ids[i])
        class_name = full_id[3:-2]
        pwd_hash = make_password(PasswordGenerator(20))
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = cnx.cursor()
        
        command = """INSERT INTO club_studentclubdata 
                     (email, username, student_id, student_real_name, 
                      is_created, is_active, is_staff, is_superuser, 
                      password, date_joined)
                     VALUES (%s,%s,%s,%s,0,0,0,0,%s,%s);"""
        val = (emails[i], uname[i], class_name, real_names[i], pwd_hash, now_str)

        cursor.execute(command, val)
        cursor.close()
        num += 1

cnx.commit()
cnx.close()
