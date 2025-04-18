import random
import csv
import os
from django.conf import settings
import club_main.settings
from club.models import StudentClubData
from record.models import *
import zipfile
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime


@login_required()
def export_record_holder(request):
    if (not (request.user.is_superuser or request.user.is_staff)):
        raise Http404
    record_holders = RecordHolderData.objects.all().values_list('name', 's_class', 'record', 'related_record', 'visibility', 'time')
    response = HttpResponse(content_type='text/csv')
    response.charset = 'utf-8-sig'
    response['Content-Disposition'] = 'attachment; filename="record_holder_data_' + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + '.csv"'
    writer = csv.writer(response)
    writer.writerow(['record_holder_name', 'record_holder_class', 'record', 'related_record', 'visibility', 'time'])
    for row in record_holders:
        r = []
        r.append(row[0])
        r.append(row[1])
        r.append(row[2])
        r.append(RecordData.objects.get(pk=row[3]).name)
        print(RecordData.objects.get(pk=row[3]).name)
        r.append(row[4])
        r.append(row[5])
        writer.writerow(r)
    return response

@login_required()
def export_record(request):
    if (not (request.user.is_superuser or request.user.is_staff)):
        raise Http404
    records = RecordData.objects.all().values_list('name', 'desc', 'type')
    response = HttpResponse(content_type='text/csv')
    response.charset = 'utf-8-sig'
    response['Content-Disposition'] = 'attachment; filename="record_data_' + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + '.csv"'
    writer = csv.writer(response)
    writer.writerow(['record_name', 'record_desc', 'record_type'])
    for row in records:
        writer.writerow(row)
    return response


def genfn():
    res = ""
    for i in range(0, 10):
        res += random.choice("qwertyuiopasdfghjklzxcvbnm1234567890")
    return res


# def addscore(name, class_id, servicename, serviceterm, servicepoint, uploaduser, desc):
#     ss = StudentClubData.objects.filter(student_real_name=name,
#                                         student_id__regex="^120%s..|^%s" % (class_id, class_id))
#     if (ss.count() == 0):
#         return "No student named %s in %s." % (name, class_id)
#     ss = ss[0]
#     ck_list = StudentDataChecker.objects.filter(user_id=ss)
#     if len(ck_list)==0:
#         tmp = StudentDataChecker(user_id=ss, data_checked=False)
#         # TODO： REFRESHING CHECKING DATA
#         tmp.save()
#     ev = ScoreEventData.objects.filter(name=servicename,
#                                        point=servicepoint)
#     if (ev.count() == 0):
#         __ = ScoreEventData(name=servicename,
#                             point=servicepoint,
#                             user_id=uploaduser)
#         __.save()
#         ev = ScoreEventData.objects.filter(name=servicename,
#                                            point=servicepoint)
#     ev = ev[0]
#     _ = StudentScoreData(user_id=ss,
#                          score_event_id=ev,
#                          date_of_addition=datetime.datetime.now(), date_of_activity=serviceterm, desc=desc)
#     _.save()
#     return "No errors."

# def is_number(s):
#     try:
#         float(s)
#         return True
#     except ValueError:
#         pass
#     try:
#         eval(s)
#         return True
#     except ValueError:
#         pass
#     try:
#         import unicodedata
#         unicodedata.numeric(s)
#         return True
#     except (TypeError, ValueError):
#         pass
    
#     return False


# def check_file(F, uploaduser):
#     fn = "tmp/" + genfn() + ".csv"
#     with open(fn, "wb") as wr:
#         for chunk in F.chunks():
#             wr.write(chunk)
#         wr.close()
#     res = ""
#     with open(fn, "r", encoding='UTF-8') as wr:
#         csv_reader = csv.reader(wr)
#         fst = True
#         for row in csv_reader:
#             if (fst):
#                 fst = False
#                 continue
#             if (len(row) % 4 != 0):
#                 res += "Csv file format wrong.\n"
#                 return res
#             student_id = row[2]
#             class_id = student_id[3:7]
#             name = row[1]
#             # print(row)
#             for i in range(4, len(row), 4):
#                 try: 
#                     servicename = row[i]
#                     if servicename == '':
#                         continue
#                     servicepoint = row[i + 1]
#                     if(not is_number(servicepoint)):
#                         res += 'Point error for %s %s where service name is %s\n' % (class_id, name, servicename)
#                     serviceterm = row[i + 2]
#                     servicedesc = row[i + 3]
#                 except Exception:
#                     res += 'Unknown Error for %s %s\n' % (class_id, name)
#         wr.close()
#     os.remove(fn)
#     return res

# def delALL(cur):
#     print(cur)
#     studentList = StudentClubData.objects.filter(student_id__regex="^120%s....|^%s.."%(cur,cur)).all()
#     for curStu in studentList:
#         tmp = StudentScoreData.objects.filter(user_id=curStu)
#         tmp.delete()
        

def process_import_record_holder(F, uploaduser):
    fn = "tmp/" + genfn() + ".csv"
    with open(fn, "wb") as wr:
        for chunk in F.chunks():
            wr.write(chunk)
        wr.close()
    # res = check_file(F,uploaduser)
    # if not res == "":
    #     return JsonResponse({'code': 0, 'message': res})
    with open(fn, "r", encoding='UTF-8') as wr:
        csv_reader = csv.reader(wr)
        for row in csv_reader:
            if row[3] == 'related_record':
                continue
            name = row[0]
            Class = row[1]
            record = row[2]
            related_record = row[3]
            visibility = row[4]
            time = row[5]
            try:
                Related_record = RecordData.objects.get(name=related_record)
            except Exception:
                return JsonResponse({'code': 0, 'message': 'Can\'t find' + related_record})
            _ = RecordHolderData(name=name,
                                    time=time,
                                    s_class=Class,
                                    record=record,
                                    related_record=Related_record,
                                    visibility=visibility)
            _.save()
        wr.close()
    os.remove(fn)
    return JsonResponse({'code': 1, 'message': 'No errors.'})


def process_import_record(F, uploaduser):
    fn = "tmp/" + genfn() + ".csv"
    with open(fn, "wb") as wr:
        for chunk in F.chunks():
            wr.write(chunk)
        wr.close()
    # res = check_file(F,uploaduser)
    # if not res == "":
    #     return JsonResponse({'code': 0, 'message': res})
    with open(fn, "r", encoding='UTF-8') as wr:
        csv_reader = csv.reader(wr)
        for row in csv_reader:
            if row[1] == 'record_desc':
                continue
            name = row[0]
            desc = row[1]
            type = row[2]
            _ = RecordData(name=name, desc=desc, type=type)
            _.save()
        wr.close()
    os.remove(fn)
    return JsonResponse({'code': 1, 'message': 'No errors.'})


@login_required()
def import_record_holder(request):
    if (not (request.user.is_superuser or request.user.is_staff)):
        raise Http404
    if (request.method == "POST"):
        return process_import_record_holder(request.FILES.get("csv", None), request.user)
    
@login_required()
def import_record(request):
    if (not (request.user.is_superuser or request.user.is_staff)):
        raise Http404
    if (request.method == "POST"):
        return process_import_record(request.FILES.get("csv", None), request.user)
