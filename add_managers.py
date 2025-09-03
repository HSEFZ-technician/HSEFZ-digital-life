# # -*- coding: utf-8 -*-
# from club.tokens import *
# # from club.models import *
# import mysql.connector

# cnx = mysql.connector.connect(
#     host='localhost',
#     port='3306',
#     user='selection_users',
#     password='123',
#     database='selection_users',
#     auth_plugin='caching_sha2_password'
# )

# eventId = 3
# groupId = 1

# cursor = cnx.cursor()

# emailList = []

# f = open('output.txt', 'r')
# for i in f.readlines():
#     emailList.append(i)

# print(emailList)

# listOfStudent = []



# # for i in listOfStudent:
# #     command = "INSERT INTO club_studentclubdata_groups (studentclubdata_id, group_id) VALUES (%d, %d);"
# #     val = (i[0], groupId)
# #     print(command % val)
#     # cursor.execute(command % val)


# # cnx.commit()
# cursor.close()
# cnx.close()


# -*- coding: utf-8 -*-
import mysql.connector

cnx = mysql.connector.connect(
    host='localhost',
    port='3306',
    user='root',
    password='abcdefg',
    database='selection_users',
    auth_plugin='caching_sha2_password',
    charset='utf8mb4',
    collation='utf8mb4_general_ci'
)

cursor = cnx.cursor()

with open('managers.txt', 'r', encoding='utf-8', errors='ignore') as f:
    email_list = [line.strip().split()[-1] for line in f if line.strip()]

for email in email_list:
    command = "UPDATE club_studentclubdata SET is_superuser=1,is_staff=1 WHERE email='%s';" % email
    cursor.execute(command)

cnx.commit()

cursor.close()
cnx.close()

print(f"Updated {len(email_list)} accounts to is_superuser=1.")
