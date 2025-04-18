import random
import csv
import os
from django.conf import settings
import club_main.settings
from youth_league.models import *
from club.models import StudentClubData
import zipfile
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
import time

def genfn():
    res = ""
    for i in range(0, 10):
        res += random.choice("qwertyuiopasdfghjklzxcvbnm1234567890")
    return res


@login_required()
def import_course_data(request):
    if (not (request.user.is_superuser or request.user.is_staff)):
        raise Http404
    if (request.method == "POST"):
        # return JsonResponse({'code': 1, 'message': process_import_add_course(request.FILES.get("csv", None), request.user)})
    # process_import_add_course(request.FILES.get("csv", None), request.user)
        return process_import_add_course(request.FILES.get("csv", None), request.user)


@login_required()
def export_course_data(request):
    if (not (request.user.is_superuser or request.user.is_staff)):
        raise Http404
    course_export = CourseData.objects.all().values_list('id', 'title', 'date', 'description')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="course_data_' + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + '.csv"'
    writer = csv.writer(response)
    writer.writerow(['course_id', 'course_title', 'course_date', 'course_description'])
    for row in course_export:
        writer.writerow(row)
    return response



def add_course(id, title, date, description):
    if (title != ""):
        entry = CourseData(id=id, title = title, date = date, description = description, creation_time = datetime.now(), update_time = datetime.now())
        entry.save()
    return "No errors."


def check_file_course_data(F, uploaduser):
    fn = "tmp/" + genfn() + ".csv"
    with open(fn, "wb") as wr:
        for chunk in F.chunks():
            wr.write(chunk)
        wr.close()
    res = ""
    with open(fn, "r", encoding='UTF-8-sig') as wr:
        csv_reader = csv.reader(wr)
        fst = True
        for row in csv_reader:
            if (fst):
                fst = False
                if(row[0] != 'course_id'):
                    res += "Csv file format wrong.\n"
                    return res
                continue
            if (len(row) != 4):
                res += "Csv file format wrong.\n"
                return res
        wr.close()
    os.remove(fn)
    return res


def process_import_add_course(F, uploaduser):
    fn = "tmp/" + genfn() + ".csv"
    with open(fn, "wb") as wr:
        for chunk in F.chunks():
            wr.write(chunk)
        wr.close()
    res = check_file_course_data(F,uploaduser)
    if not res == "":
        return JsonResponse({'code': 0, 'message': res})
    CourseData.objects.all().delete()
    with open(fn, "r", encoding='UTF-8-sig') as wr:
        csv_reader = csv.reader(wr)
        fst = True
        for row in csv_reader:
            if (fst):
                fst = False
                continue
            if (row[0] == ""):
                continue
            course_id = row[0]
            course_title = row[1]
            course_date = datetime.strptime(row[2], '%Y-%m-%d')
            # course_date = row[2]
            print(course_date)
            course_description = row[3]
            ads = add_course(course_id, course_title, course_date, course_description)
        wr.close()
    os.remove(fn)
    return JsonResponse({'code': 1, 'message': '数据更新成功'})






@login_required()
def import_course_score_data(request):
    if (not (request.user.is_superuser or request.user.is_staff)):
        raise Http404
    if (request.method == "POST"):
        return process_import_add_course_score(request.FILES.get("csv", None), request.user)
    

@login_required()
def export_course_score_data(request):
    if (not (request.user.is_superuser or request.user.is_staff)):
        raise Http404
    course_score_export = CourseAssignmentScore.objects.all().values_list('course_id', 'stu_id', 'score')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="course_score_' + datetime.now().strftime("%d-%m-%Y %H:%M:%S") + '.csv"'
    writer = csv.writer(response)
    writer.writerow(['course_id', 'stu_id', 'score'])
    for row in course_score_export:
        modified = list(row)
        stu_no = StudentClubData.objects.filter(id=row[1]).values('student_id')[0]['student_id']
        modified[1] = stu_no
        writer.writerow(modified)
    return response



def add_course_score(course_id, stu_id, score):
    if (stu_id != ""):
        entry = CourseAssignmentScore(stu_id = stu_id, course_id = course_id, score = score, creation_time = datetime.now(), update_time = datetime.now())
        entry.save()
    return "No errors."


def check_file_course_score(F, uploaduser):
    fn = "tmp/" + genfn() + ".csv"
    with open(fn, "wb") as wr:
        for chunk in F.chunks():
            wr.write(chunk)
        wr.close()
    res = ""
    with open(fn, "r", encoding='UTF-8-sig') as wr:
        csv_reader = csv.reader(wr)
        fst = True
        for row in csv_reader:
            if (fst):
                fst = False
                continue
            if (len(row) != 3):
                res += "Csv file format wrong.\n"
                return res
        wr.close()
    os.remove(fn)
    return res

def process_import_add_course_score(F, uploaduser):
    fn = "tmp/" + genfn() + ".csv"
    with open(fn, "wb") as wr:
        for chunk in F.chunks():
            wr.write(chunk)
        wr.close()
    res = check_file_course_score(F,uploaduser)
    if not res == "":
        return JsonResponse({'code': 0, 'message': res})
    CourseAssignmentScore.objects.all().delete()
    with open(fn, "r", encoding='UTF-8') as wr:
        csv_reader = csv.reader(wr)
        fst = True
        for row in csv_reader:
            if (fst):
                fst = False
                continue
            if (row[0] == ""):
                continue
            course_id = row[0]
            stu_id = StudentClubData.objects.filter(student_real_name=row[1]).values('id')[0]['id']
            score = row[2]
            print(stu_id)
            ads = add_course_score(course_id, stu_id, score)
        wr.close()
    os.remove(fn)
    return JsonResponse({'code': 1, 'message': '数据更新成功'})









@login_required()
def import_test_data(request):
    if (not (request.user.is_superuser or request.user.is_staff)):
        raise Http404
    if (request.method == "POST"):
        return process_import_add_test(request.FILES.get("csv", None), request.user)


@login_required()
def export_test_data(request):
    if (not (request.user.is_superuser or request.user.is_staff)):
        raise Http404
    test_export = TestData.objects.all().values_list('id', 'title', 'date', 'description')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="test_data_' + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + '.csv"'
    writer = csv.writer(response)
    writer.writerow(['test_id', 'test_title', 'test_date', 'test_description'])
    for row in test_export:
        writer.writerow(row)
    return response



def add_test(id, title, date, description):
    if (title != ""):
        entry = TestData(id = id, title = title, date = date, description = description, creation_time = datetime.now(), update_time = datetime.now())
        entry.save()
    return "No errors."


def check_file_test_data(F, uploaduser):
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
                if(row[0] != 'test_id'):
                    res += "Csv file format wrong.\n"
                    return res
                continue
            if (len(row) != 4):
                res += "Csv file format wrong.\n"
                return res
        wr.close()
    os.remove(fn)
    return res


def process_import_add_test(F, uploaduser):
    fn = "tmp/" + genfn() + ".csv"
    with open(fn, "wb") as wr:
        for chunk in F.chunks():
            wr.write(chunk)
        wr.close()
    res = check_file_test_data(F,uploaduser)
    if not res == "":
        return JsonResponse({'code': 0, 'message': res})
    TestData.objects.all().delete()
    with open(fn, "r", encoding='UTF-8') as wr:
        csv_reader = csv.reader(wr)
        fst = True
        for row in csv_reader:
            if (fst):
                fst = False
                continue
            if (row[0] == ""):
                continue
            test_id = row[0]
            test_title = row[1]
            test_date = datetime.strptime(row[2], '%Y/%m/%d')
            # test_date = row[2]
            course_description = row[3]
            ads = add_test(test_id, test_title, test_date, course_description)
        wr.close()
    os.remove(fn)
    return JsonResponse({'code': 1, 'message': '数据更新成功'})









@login_required()
def import_test_score_data(request):
    if (not (request.user.is_superuser or request.user.is_staff)):
        raise Http404
    if (request.method == "POST"):
        return process_import_add_test_score(request.FILES.get("csv", None), request.user)
    

@login_required()
def export_test_score_data(request):
    if (not (request.user.is_superuser or request.user.is_staff)):
        raise Http404
    test_score_export = TestScore.objects.all().values_list('test_id', 'stu_id', 'score')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="test_score_' + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + '.csv"'
    writer = csv.writer(response)
    writer.writerow(['test_id', 'stu_id', 'score'])
    for row in test_score_export:
        modified = list(row)
        stu_no = StudentClubData.objects.filter(id=row[1]).values('student_id')[0]['student_id']
        modified[1] = stu_no
        writer.writerow(modified)
    return response



def add_test_score(test_id, stu_id, score):
    print(1)
    if (stu_id != ""):
        entry = TestScore(stu_id = stu_id, test_id = test_id, score = score, creation_time = datetime.now(), update_time = datetime.now())
        entry.save()
    return "No errors."


def check_file_test_score(F, uploaduser):
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
            if (len(row) != 3):
                res += "Csv file format wrong.\n"
                return res
        wr.close()
    os.remove(fn)
    return res

def process_import_add_test_score(F, uploaduser):
    fn = "tmp/" + genfn() + ".csv"
    with open(fn, "wb") as wr:
        for chunk in F.chunks():
            wr.write(chunk)
        wr.close()
    res = check_file_test_score(F,uploaduser)
    if not res == "":
        return JsonResponse({'code': 0, 'message': res})
    TestScore.objects.all().delete()
    with open(fn, "r", encoding='UTF-8') as wr:
        csv_reader = csv.reader(wr)
        fst = True
        for row in csv_reader:
            if (fst):
                fst = False
                continue
            if (row[0] == ""):
                continue
            test_id = row[0]
            stu_id = StudentClubData.objects.filter(student_id=row[1]).values('id')[0]['id']
            score = row[2]
            ads = add_test_score(test_id, stu_id, score)
        wr.close()
    os.remove(fn)
    return JsonResponse({'code': 1, 'message': '数据更新成功'})