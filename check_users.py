# # -*- coding: utf-8 -*-
# import pandas as pd
# import os
# import csv
# from club.tokens import *
# # from club.models import *
# import mysql.connector

# cnx = mysql.connector.connect(
#     host='localhost',
#     port='3306',
#     user='root',
#     password='DB40x1Yc#3:2',
#     database='selection_users',
#     auth_plugin='caching_sha2_password'
# )

# eventId = 9

# listOfCourse = []

# cursor = cnx.cursor()
# cursor.execute("SELECT id,name from club_eventclassinformation where event_id_id=%d"%eventId)
# listOfCourse = cursor.fetchall()
# cursor.execute("SELECT id,student_real_name,student_id,email from club_studentclubdata where student_id REGEXP \'^25\' or student_id REGEXP \'^26\' or student_id REGEXP \'^12025\'")
# listOfStudent = cursor.fetchall()

# dic = {}
# mnum = 0 
# for i in listOfStudent:
#     tmpList = list(i)
#     mnum = max(mnum, tmpList[0])
#     dic[tmpList[0]] = 1
    
# mnum +=10

# CounterList = []
# for i in range(mnum):
#     CounterList.append(0)

# # print(listOfStudent)

# for i,name in listOfCourse:
#     cursor.execute("SELECT info_id_id,user_id_id from club_studentselectioninformation where info_id_id=%d"%i)
#     li = cursor.fetchall()
#     IDList = []
#     for i in li:
#         tmpList = list(i)
#         IDList.append(tmpList[1])
#         CounterList[tmpList[1]]+=1
#     data = []
#     for user_id in IDList:
#         cursor.execute("SELECT id,student_real_name,student_id,email from club_studentclubdata where id=%d"%user_id)
#         tmp = cursor.fetchall()
#         for x in tmp:
#             data.append(list(x))

#     with open('output/%s.csv'%name, 'w', newline='') as newfile:
#         writer = csv.writer(newfile)
        
#         writer.writerow(['ID', 'Name', 'Class/ID', 'Email'])
#         writer.writerows(data)


# # print(dic)

# errorList = []
# emptyList = []

# for i, cnt in enumerate(CounterList):
#     if not(i in dic):
#         continue
#     if cnt > 1:
#         errorList.append(i)
#     if cnt ==0:
#         emptyList.append(i)

# data = []
# for user_id in errorList:
#     cursor.execute("SELECT id,student_real_name,student_id,email from club_studentclubdata where id=%d"%user_id)
#     tmp = cursor.fetchall()
#     for x in tmp:
#         data.append(list(x))

# with open('output/ERROR.csv', 'w', newline='') as newfile:
#     writer = csv.writer(newfile)
    
#     writer.writerow(['ID', 'Name', 'Class/ID', 'Email'])
#     writer.writerows(data)
    
# data.clear()
# for user_id in emptyList:
#     cursor.execute("SELECT id,student_real_name,student_id,email from club_studentclubdata where id=%d"%user_id)
#     tmp = cursor.fetchall()
#     for x in tmp:
#         data.append(list(x))

# with open('output/EMPTY.csv', 'w', newline='') as newfile:
#     writer = csv.writer(newfile)
    
#     writer.writerow(['ID', 'Name', 'Class/ID', 'Email'])
#     writer.writerows(data)

# cursor.close()
# cnx.close()


# -*- coding: utf-8 -*-
import os
import csv
import mysql.connector

os.makedirs("output", exist_ok=True)

cnx = mysql.connector.connect(
    host='localhost',
    port='3306',
    user='root',
    password='abcdefg',
    database='selection_users',
    auth_plugin='caching_sha2_password'
)

cursor = cnx.cursor()

eventId = 9

query = """
SELECT stu.id,
       stu.student_real_name,
       stu.student_id,
       stu.email,
       e.name AS club_name
FROM club_studentselectioninformation sel
JOIN club_eventclassinformation e
  ON sel.info_id_id = e.id
JOIN club_studentclubdata stu
  ON sel.user_id_id = stu.id
WHERE e.event_id_id = %s
ORDER BY e.name, stu.student_real_name
"""
cursor.execute(query, (eventId,))
rows = cursor.fetchall()

output_file = f"output/event_{eventId}_selection_info.csv"
with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["StudentDB_ID", "Name", "StudentID", "Email", "ClubName"])
    writer.writerows(rows)

cursor.close()
cnx.close()
