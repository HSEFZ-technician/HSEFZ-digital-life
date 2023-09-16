# -*- coding: utf-8 -*-
from club.tokens import *
# from club.models import *
import mysql.connector

cnx = mysql.connector.connect(
    host='localhost',
    port='3306',
    user='selection_users',
    password='123',
    database='selection_users',
    auth_plugin='caching_sha2_password'
)

eventId = 3
groupId = 1

cursor = cnx.cursor()

emailList = []

f = open('output.txt', 'r')
for i in f.readlines():
    emailList.append(i)

print(emailList)

listOfStudent = []



# for i in listOfStudent:
#     command = "INSERT INTO club_studentclubdata_groups (studentclubdata_id, group_id) VALUES (%d, %d);"
#     val = (i[0], groupId)
#     print(command % val)
    # cursor.execute(command % val)


# cnx.commit()
cursor.close()
cnx.close()
