# -*- coding: utf-8 -*-
import pandas as pd
import os
from club.tokens import *
# from club.models import *
import mysql.connector
from django.contrib.auth.hashers import make_password
import datetime

cnx = mysql.connector.connect(
    host='localhost',
    port='3306',
    user='root',
    password='123',
    database='selection_users',
)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'club_main.settings')


num = 1475
import getpass
email = input("Email: ")
username = input("Username: ")
class_name = input("Class name: ")
student_real_name = input("Student real name (Chinese): ")
password1 = getpass.getpass("Password: ")
password2 = getpass.getpass("Password (Confirm): ")
if (password1 != password2):
  print("Passwords do not match!")
  exit(0)
cursor = cnx.cursor()
command = "INSERT INTO club_studentclubdata (email, username, student_id, student_real_name, is_created, is_active, is_staff, is_superuser, password, date_joined) VALUES (\'%s\', \'%s\', \'%s\', \'%s\', 1,1,1,1, \'%s\', \'%s\');"
val = (email, username, class_name,
       student_real_name, make_password(password1), str(datetime.datetime.now()).split(".")[0])
num += 1
cursor.execute(command % val)
cursor.close()

cnx.commit()

# for i in range(num):
#     if i <= 5:
#         continue
#     cursor = cnx.cursor()
#     command = "INSERT INTO club_studentclubdata_groups (studentclubdata_id, group_id) VALUES (%d, 2);"
#     val = (i)
#     print(command % val)
#     cursor.execute(command % val)
#     cursor.close()

cnx.commit()
cnx.close()
