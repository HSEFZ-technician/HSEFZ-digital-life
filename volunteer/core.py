import random
import csv
import os
from django.conf import settings
import club_main.settings
from club.models import StudentClubData
from volunteer.models import StudentScoreData, ScoreEventData, StudentDataChecker
import zipfile
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
import datetime


@login_required()
def export(request):
    if (not (request.user.is_superuser or request.user.is_staff)):
        raise Http404
    students = StudentClubData.objects.all()
    map = {}
    cur = 0
    listOfGrades = []
    listOfAll = [[], [], []]
    for i in students:
        if i.student_id == '000000000':
            continue
        listStudent = []
        listStudent.append(i.student_id)
        listStudent.append(i.student_real_name)
        check_name = "未确认"
        check_item = StudentDataChecker.objects.filter(user_id=i)
        if len(check_item) != 0:
            if check_item[0].data_checked:
                check_name = "已确认"
        listStudent.append(check_name)
        events = StudentScoreData.objects.filter(user_id=i).all()
        for j in events:
            eventDetail = j.score_event_id
            listStudent.append(eventDetail.name)
            listStudent.append(eventDetail.point)
            listStudent.append(j.date_of_activity)
            listStudent.append(j.desc)
        curGrade = ''
        if len(i.student_id)!=9:
            curGrade = i.student_id[0:2]
        else:
            curGrade = i.student_id[3:5]
        if map.get(curGrade) == None:
            listOfGrades.append(curGrade)
            map[curGrade] = cur
            listOfAll[cur].append(["班级", "姓名","课时确认","服务1", "课时数1", "时间1", "描述", "服务2", "课时数2", "时间2", "描述", "服务3",
                                  "课时数3", "时间3", "描述", "服务4", "课时数4", "时间4", "描述", "服务5", "课时数5", "时间5", "描述", "服务6", "课时数6", "时间6", "描述",])
            cur += 1
        listOfAll[map[curGrade]].append(listStudent)
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


def addscore(name, class_id, student_id, servicename, serviceterm, servicepoint, uploaduser, desc):
    ss = StudentClubData.objects.filter(student_real_name=name,
                                        student_id__regex="^%s|^%s" % (student_id, class_id))
    if (ss.count() == 0):
        return "No student named %s in %s." % (name, class_id)
    ss = ss[0]
    ck_list = StudentDataChecker.objects.filter(user_id=ss)
    if len(ck_list)==0:
        tmp = StudentDataChecker(user_id=ss, data_checked=False)
        # TODO： REFRESHING CHECKING DATA
        tmp.save()
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

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        eval(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    
    return False


def check_file(F, uploaduser):
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
            if (len(row) % 4 != 0):
                res += "Csv file format wrong.\n"
                return res
            student_id = row[2]
            class_id = student_id[3:7]
            name = row[1]
            # print(row)
            for i in range(4, len(row), 4):
                try: 
                    servicename = row[i]
                    if servicename == '':
                        continue
                    servicepoint = row[i + 1]
                    if(not is_number(servicepoint)):
                        res += 'Point error for %s %s where service name is %s\n' % (class_id, name, servicename)
                    serviceterm = row[i + 2]
                    servicedesc = row[i + 3]
                except Exception:
                    res += 'Unknown Error for %s %s\n' % (class_id, name)
        wr.close()
    os.remove(fn)
    return res

def delALL(cur):
    studentList = StudentClubData.objects.filter(student_id__regex="^120%s....|^%s.."%(cur,cur)).all()
    print(len(studentList))
    for curStu in studentList:
        tmp = StudentScoreData.objects.filter(user_id=curStu)
        tmp.delete()


def delSINGLE(cur, cur_name):
    cur_grade = cur[3:7]
    # print(cur, cur_grade, cur_name)
    studentList = StudentClubData.objects.filter(student_id__regex="^%s|^%s"%(cur,cur_grade), student_real_name=cur_name).all()
    print(len(studentList))
    for curStu in studentList:
        tmp = StudentScoreData.objects.filter(user_id=curStu)
        # print(len(tmp))
        tmp.delete()
        

def process_import_file(F, uploaduser):
    fn = "tmp/" + genfn() + ".csv"
    with open(fn, "wb") as wr:
        for chunk in F.chunks():
            wr.write(chunk)
        wr.close()
    res = check_file(F,uploaduser)
    if not res == "":
        return JsonResponse({'code': 0, 'message': res})
    with open(fn, "r", encoding='UTF-8') as wr:
        csv_reader = csv.reader(wr)
        fst = True
        secd = False
        for row in csv_reader:
            if (fst):
                fst = False
                secd = True
                continue
            if secd:
                student_id = row[2]
                cur = student_id[3:5]
                # delALL(cur)
                secd = False
            student_id = row[2]
            class_id = student_id[3:7]
            name = row[1]
            if name=='':
                # print(111)
                continue
            delSINGLE(student_id, name)
            for i in range(4, len(row), 4):
                servicename = row[i]
                if servicename == '':
                    continue
                servicepoint = float(eval(row[i + 1]))
                serviceterm = row[i + 2]
                servicedesc = row[i + 3]
                ads = addscore(name, class_id,student_id, servicename,
                               serviceterm, servicepoint, uploaduser, servicedesc)
        wr.close()
    os.remove(fn)
    return JsonResponse({'code': 1, 'message': 'No errors.'})


@login_required()
def Import(request):
    if (not (request.user.is_superuser or request.user.is_staff)):
        raise Http404
    if (request.method == "POST"):
        return process_import_file(request.FILES.get("csv", None), request.user)
