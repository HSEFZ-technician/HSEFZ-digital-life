import csv
import os
from django.conf import settings
import club_main.settings
from club.models import StudentClubData
from volunteer.models import StudentScoreData, ScoreEventData
import zipfile
from django.http import FileResponse

def export(request):
    students = StudentClubData.objects.all()
    map = {}
    cur = 0
    listOfGrades = []
    listOfAll = [[],[],[]]
    for i in students:
        listStudent = []
        listStudent.append(i.student_id)
        listStudent.append(i.student_real_name)
        events = StudentScoreData.objects.filter(user_id=i).all()
        for j in events:
            eventDetail = j.score_event_id
            listStudent.append(eventDetail.name)
            listStudent.append(eventDetail.point)
            listStudent.append(eventDetail.desc)
        if map.get(i.student_id[0:2]) == None:
            listOfGrades.append(i.student_id[0:2])
            map[i.student_id[0:2]] = cur
            listOfAll[cur].append(["班级","姓名","服务1","课时数1","时间1","服务2","课时数2","时间2","服务3","课时数3","时间3","服务4","课时数4","时间4","服务5","课时数5","时间5",])
            cur+=1
        listOfAll[map[i.student_id[0:2]]].append(listStudent)
    pathList = []
    for i in listOfGrades:
        csvPath = os.path.join(club_main.settings.MEDIA_ROOT, "%s.csv" % i)
        pathList.append(csvPath)
        with open(csvPath, 'w', newline='') as newfile:
            writer = csv.writer(newfile)
            writer.writerows(listOfAll[map[i]])
    with zipfile.ZipFile(os.path.join(club_main.settings.MEDIA_ROOT, "outputs.zip"), 'w') as z:
        for f in pathList:
            z.write(f,arcname=os.path.basename(f))
    response = FileResponse(open(os.path.join(club_main.settings.MEDIA_ROOT, "outputs.zip"), 'rb'))
    return response
