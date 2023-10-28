import random
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
    listOfAll = [[], [], []]
    for i in students:
        listStudent = []
        listStudent.append(i.student_id)
        listStudent.append(i.student_real_name)
        events = StudentScoreData.objects.filter(user_id=i).all()
        for j in events:
            eventDetail = j.score_event_id
            listStudent.append(eventDetail.name)
            listStudent.append(eventDetail.point)
            listStudent.append(j.date_of_activity)
            listStudent.append(j.desc)
        if map.get(i.student_id[0:2]) == None:
            listOfGrades.append(i.student_id[0:2])
            map[i.student_id[0:2]] = cur
            listOfAll[cur].append(["班级", "姓名", "服务1", "课时数1", "时间1", "描述", "服务2", "课时数2", "时间2", "描述", "服务3",
                                  "课时数3", "时间3", "描述", "服务4", "课时数4", "时间4", "描述", "服务5", "课时数5", "时间5", "描述", "服务6", "课时数6", "时间6", "描述",])
            cur += 1
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
            z.write(f, arcname=os.path.basename(f))
    response = FileResponse(
        open(os.path.join(club_main.settings.MEDIA_ROOT, "outputs.zip"), 'rb'))
    return response


def genfn():
    res = ""
    for i in range(0, 10):
        res += random.choice("qwertyuiopasdfghjklzxcvbnm1234567890")
    return res


def addscore(name, class_id, servicename, serviceterm, servicepoint, uploaduser, desc):
    ss = StudentClubData.objects.filter(student_real_name=name,
                                        student_id=class_id)
    if (ss.count() == 0):
        return "No student named %s in %s." % (name, class_id)
    ss = ss[0]
    ev = ScoreEventData.objects.filter(name=servicename,
                                       point=servicepoint)
    if (ev.count() == 0):
        __ = ScoreEventData(name=servicename,
                            point=servicepoint,
                            user_id=uploaduser)
        __.save()
        ev = ScoreEventData.objects.filter(name=servicename,
                                           point=servicepoint)
    ev = ev[0]
    _ = StudentScoreData(user_id=ss,
                         score_event_id=ev,
                         date_of_addition=datetime.datetime.now(), date_of_activity=serviceterm, desc=desc)
    _.save()
    return "No errors."


def process_import_file(F, uploaduser):
    fn = "tmp/" + genfn() + ".csv"
    with open(fn, "wb") as wr:
        for chunk in F.chunks():
            wr.write(chunk)
        wr.close()
    res = ""
    with open(fn, "r", encoding='UTF-8') as wr:
        csv_reader = csv.reader(wr)
        fst = True
        for row in csv_reader:
            if (fst):
                fst = False
                continue
            if (len(row) % 4 != 3):
                res += "Csv file format wrong.\n"
                continue
            student_id = row[1]
            class_id = student_id[3:7]
            # print(class_id)
            name = row[2]
            print(row)
            for i in range(3, len(row), 4):
                servicename = row[i]
                if servicename == '':
                    continue
                servicepoint = float(eval(row[i + 1]))
                serviceterm = row[i + 2]
                servicedesc = row[i + 3]
                ads = addscore(name, class_id, servicename,
                               serviceterm, servicepoint, uploaduser, servicedesc)
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
