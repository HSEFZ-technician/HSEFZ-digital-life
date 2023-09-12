# -*- coding: utf-8 -*-
import pandas as pd
import os

fileList = os.listdir('data')
# print(fileList)

for i in fileList:
    path = 'data/' + i
    class_name = i[0:i.find('.')]
    # print(class_name)
    csvFile = pd.read_csv(path, encoding='gb18030')
    real_names = csvFile['名称']
    emails = csvFile['电子邮件地址']
    date = csvFile['修改时间']
    uname = []
    for j in emails:
        atC = j.find('@')
        substr = j[0:atC]
        uname.append(substr)

    for j in real_names:
        for k in j:
            if k>='0' and k<='9': 
                print('ERROR at %s with name %s' % (class_name, j))
                break
