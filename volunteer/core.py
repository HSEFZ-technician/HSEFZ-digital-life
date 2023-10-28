import csv
import os
from django.conf import settings
import club_main.settings
from club.models import StudentClubData
from volunteer.models import StudentScoreData, ScoreEventData
import zipfile
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
import datetime

@login_required()
def export(request):
    if (not request.user.is_superuser):
        raise Http404
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
            listOfAll[cur].append(["班级","姓名","服务1","课时数1","时间1","服务2","课时数2","时间2","服务3","课时数3","时间3","服务4","课时数4","时间4","服务5","课时数5","时间5","服务6","课时数6","时间6",])
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

import random
def genfn():
    res = ""
    for i in range(0, 10):
        res += random.choice("qwertyuiopasdfghjklzxcvbnm1234567890")
    return res

def addscore(name, class_id, servicename, serviceterm, servicepoint, uploaduser):
    ss = StudentClubData.objects.filter(student_real_name = name,
                                        student_id = class_id)
    if (ss.count() == 0):
        return "No student named %s in %s." % (name, class_id)
    ss = ss[0]
    ev = ScoreEventData.objects.filter(name = servicename,
                                       desc = serviceterm,
                                       point = servicepoint)
    if (ev.count() == 0):
        __ = ScoreEventData(name = servicename,
                            desc = serviceterm,
                            point = servicepoint,
                            user_id = uploaduser)
        __.save()
        ev = ScoreEventData.objects.filter(name = servicename,
                                           desc = serviceterm,
                                           point = servicepoint)
    ev = ev[0]
    _ = StudentScoreData(user_id = ss,
                         score_event_id = ev,
                         date_of_addition = datetime.datetime.now())
    _.save()
    return "No errors."

def process_import_file(F, uploaduser):
    fn = "tmpdata/" + genfn() + ".csv"
    with open(fn, "wb") as wr:
        for chunk in F.chunks():
            wr.write(chunk)
        wr.close()
    res = ""
    with open(fn, "r") as wr:
        csv_reader = csv.reader(wr)
        fst = True
        for row in csv_reader:
            if (fst):
                fst = False
                continue
            if (len(row) % 3 != 2):
                res += "Csv file format wrong.\n"
                continue
            class_id = row[0]
            name = row[1]
            for i in range(2, len(row), 3):
                servicename = row[i]
                servicepoint = int(row[i + 1])
                serviceterm = row[i + 2]
                ads = addscore(name, class_id, servicename, serviceterm, servicepoint, uploaduser)
                if (ads != "No errors."):
                    res += ads
                    res += '\n'
        wr.close()
    os.remove(fn)
    if (res == ""):
        return JsonResponse({'code': 1, 'message': 'No errors.'})
    return JsonResponse({'code': 0, 'message': res})

@login_required()
def Import(request):
    if (not request.user.is_superuser):
        raise Http404
    if (request.method == "POST"):
        return process_import_file(request.FILES.get("csv", None), request.user)
