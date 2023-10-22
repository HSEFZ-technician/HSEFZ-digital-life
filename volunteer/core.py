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
        listStudent.append(i.student_real_name)
        listStudent.append(i.student_id)
        events = StudentScoreData.objects.filter(user_id=i).all()
        for j in events:
            listItem = []
            eventDetail = j.score_event_id
            listItem.append(eventDetail.name)
            listItem.append(eventDetail.point)
            listItem.append(j.date_of_addition)
            listStudent.append(listItem)
        if map.get(i.student_id[0:2]) == None:
            listOfGrades.append(i.student_id[0:2])
            map[i.student_id[0:2]] = cur
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