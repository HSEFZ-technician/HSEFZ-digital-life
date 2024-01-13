# -*- coding: utf-8 -*-
from club.tokens import *
import csv
# from club.models import *
import mysql.connector

cnx = mysql.connector.connect(
    host='localhost',
    port='3306',
    user='root',
    password='123',
    database='selection_users',
    auth_plugin='caching_sha2_password'
)

cursor = cnx.cursor()

with open('26.csv', 'r', encoding='UTF-8') as wr:
    csv_reader = csv.reader(wr)
    fst = True
    for row in csv_reader:
        if (fst):
            fst = False
            continue
        student_id = row[2]
        class_id = student_id[3:7]
        name = row[1]
        if name == '' or student_id =='':
            continue
        command = "UPDATE club_studentclubdata SET student_id=\'%s\' WHERE student_id='\%s\' and student_real_name=\'%s\';" % (student_id,class_id,name)
        # print(command)
        cursor.execute(command)
    



# for i in listOfStudent:
#     command = "INSERT INTO club_studentclubdata_groups (studentclubdata_id, group_id) VALUES (%d, %d);"
#     val = (i[0], groupId)
#     print(command % val)
    # cursor.execute(command % val)


cnx.commit()
cursor.close()
cnx.close()
