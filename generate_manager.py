import os

f = open('managers.txt', 'r', encoding='utf-8', errors='ignore')

email_list = []

for i in f.readlines():
    substr = i[i.find(' ', i.find(' ')+1)+1:]
    while substr.startswith(' '):
        substr = substr[1:]
    while substr.endswith(' ') or substr.endswith('\n'):
        substr = substr[:-1]
    email_list.append(substr)

# template = 'UPDATE club_studentclubdata SET is_staff=1 WHERE '

template = ''

for i in email_list:
    template = template + i + '\n'
#     template = template + 'email=\'' + i + '\' or '
# template += ';'


tm = open('output.txt', 'a+')
tm.write(template)
f.close()
tm.close()
print(template)
