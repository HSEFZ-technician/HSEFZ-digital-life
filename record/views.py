import datetime
from record.models import RecordData
from record.models import RecordHolderData
from record.forms import ModifyRecordForm, ModifyRecordHolderForm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404, HttpResponseRedirect
from record.core import *
import json
from datetime import timedelta

# Create your views here.

def index(request):
    return render(request, 'record/home.html', {'title': 'EFZ数字生活·华二之“最”'})

def sport_record(request):
    records = RecordData.objects.all()
    recordHolders = RecordHolderData.objects.all()
    form = []
    form_h = []

    for m in records:
        i = {}
        if m.type == "体育之最":
            i['id'] = m.pk
            i['name'] = m.name
            i['desc'] = m.desc
            form.append(i)
        else:
            continue

    for n in recordHolders:
        j = {}
        j['id'] = n.pk
        j['name'] = n.name
        j['s_class'] = n.s_class
        j['related_record'] = n.related_record.pk
        j['record'] = n.record
        j['time'] = (n.time + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
        j['visibility'] = n.visibility
        form_h.append(j)

    if len(form) == 0:
        return render(request, 'record/record.html', {'isEmpty': True})

    return render(request, 'record/record.html', {'form': form, 'form_h': form_h, 'title': 'EFZ数字生活·EFZ之“最”'})

def fun_record(request):
    records = RecordData.objects.all()
    recordHolders = RecordHolderData.objects.all()
    form = []
    form_h = []

    for m in records:
        i = {}
        if m.type == "趣味之最":
            i['id'] = m.pk
            i['name'] = m.name
            i['desc'] = m.desc
            form.append(i)
        else:
            continue

    for n in recordHolders:
        j = {}
        j['id'] = n.pk
        j['name'] = n.name
        j['s_class'] = n.s_class
        j['related_record'] = n.related_record.pk
        j['record'] = n.record
        j['time'] = (n.time + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
        j['visibility'] = n.visibility
        form_h.append(j)

    if len(form) == 0:
        return render(request, 'record/record.html', {'isEmpty': True})

    return render(request, 'record/record.html', {'form': form, 'form_h': form_h, 'title': 'EFZ数字生活·EFZ之“最”'})


@login_required()
def record_manage(request):
    modify_record_url = '/record/modify_record'

    if (not (request.user.is_superuser or request.user.is_staff)):
        raise Http404

    _s = RecordData.objects.all()
    table_content = "<tr><td><a href='%s?id=%d'>%s</a></td><td>%s</td><td>%s</td></tr>"
    cs = []
    for _ in _s:
        cs.append(table_content %
                  (modify_record_url, _.pk, _.name, _.desc, _.type))
    cs.sort(key=lambda x: x[0])
    table_div = ''
    for i in cs:
        table_div += i

    return render(request, 'record/record_manage.html',
                  {'title': '纪录管理', 'now_record_manage': True, 'table_div': table_div})


@login_required()
def record_holder_manage(request):
    modify_record_url = '/record/modify_record_holder'

    if (not (request.user.is_superuser or request.user.is_staff)):
        raise Http404

    _s = RecordHolderData.objects.all()
    table_content = "<tr><td><a href='%s?id=%d'>%s</a></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
    cs = []
    for _ in _s:
        cs.append(table_content %
                  (modify_record_url, _.pk, _.name, _.s_class, _.related_record.name, _.record, 
                  (_.time + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"), _.visibility))
    cs.sort(key=lambda x: x[0])
    table_div = ''
    for i in cs:
        table_div += i

    return render(request, 'record/record_holder_manage.html',
                  {'title': '纪录保持者管理', 'now_record_holder_manage': True, 'table_div': table_div})


@login_required()
def create_record(request):
    cap = request.user.is_superuser or request.user.is_staff
    # classes = [(i.pk, i.name)
    #            for i in ClassTeamData.objects.all()]

    if (not cap):
        raise Http404

    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode())
            typename = json_data['type']
            if typename == "new":
                form = ModifyRecordForm({}, json_data['data'])
                # print(form.data)
                _ = RecordData(name=form.data['name'],desc=form.data['desc'],type=form.data['type'])
                _.save()
                return JsonResponse({'code': 1, 'message': '新建成功'})
            else:
                return JsonResponse({'code': 0, 'message': '请求非法'})
        except Exception as e:
            print(e)
            return JsonResponse({'code': 0, 'message': '数据非法或发生了错误'})

    form = ModifyRecordForm({})
    return render(request, 'record/create_record.html', {'title': '创建纪录', 'form': form})


@login_required()
def create_record_holder(request):
    cap = request.user.is_superuser or request.user.is_staff
    classes = [(i.pk, i.name)
               for i in RecordData.objects.all()]

    if (not cap):
        raise Http404

    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode())
            typename = json_data['type']
            if typename == "new":
                form = ModifyRecordHolderForm(classes, {}, json_data['data'])
                if 'visibility' in json_data['data']:
                    V = True
                else:
                    V = False
                _ = RecordHolderData(name=form.data['name'],
                                    time=datetime.strptime(form.data['time'], '%Y-%m-%d %H:%M:%S'),
                                    s_class=form.data['s_class'],
                                    record=form.data['record'],
                                    related_record=RecordData.objects.get(pk=form.data['related_record']),
                                    visibility=V)
                _.save()
                return JsonResponse({'code': 1, 'message': '新建成功'})
            else:
                return JsonResponse({'code': 0, 'message': '请求非法'})
        except Exception as e:
            print(e)
            return JsonResponse({'code': 0, 'message': '数据非法或发生了错误'})

    form = ModifyRecordHolderForm(classes, {})
    return render(request, 'record/create_record_holder.html', {'title': '创建纪录保持者', 'form': form})


@login_required()
def modify_record(request):
    record_id = request.GET.get('id', None)
    try:
        _ = RecordData.objects.get(pk=record_id)
    except Exception as e:
        raise Http404

    cap = request.user.is_superuser or request.user.is_staff
    if (not cap):
        raise Http404

    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode())
            typename = json_data['type']
            print(json_data)
            if typename == 'save':
                form = ModifyRecordForm({}, json_data['data'])
                rec = _
                if form.is_valid():
                    rec.name = form.cleaned_data['name']
                    rec.desc = form.cleaned_data['desc']
                    rec.type = form.cleaned_data['type']
                    print(rec.type)
                    print(form.cleaned_data['type'])
                    rec.save()
                    return JsonResponse({'code': 1, 'message': '保存成功'})
                else:
                    return JsonResponse({'code': 0, 'message': '表单非法'})
            elif typename == 'delete':
                rec = _
                rec.delete()
                return JsonResponse({'code': 1, 'message': '删除成功'})
            else:
                return JsonResponse({'code': 0, 'message': '请求非法'})
        except Exception as e:
            print(e)
            return JsonResponse({'code': 0, 'message': '数据非法或发生了错误'})

    rec = _
    form = ModifyRecordForm({'name': rec.name, 'desc': rec.desc, 'type': rec.type})

    return render(request, 'record/modify_record.html', {'title': '修改纪录 - %s' % rec.name, 'now_record_manage': True,
                                                         'form': form,
                                                         'now_modify_record': True,
                                                         'has_value': False
                                                         })

@login_required()
def modify_record_holder(request):
    record_holder_id = request.GET.get('id', None)
    try:
        _ = RecordHolderData.objects.get(pk=record_holder_id)
    except Exception as e:
        raise Http404

    cap = request.user.is_superuser or request.user.is_staff
    if (not cap):
        raise Http404
    
    classes = [(i.pk, i.name)
               for i in RecordData.objects.all()]

    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode())
            typename = json_data['type']
            if typename == 'save':
                form = ModifyRecordHolderForm(classes, {}, json_data['data'])
                rec = _
                if form.is_valid():
                    rec.name = form.cleaned_data['name']
                    rec.s_class = form.cleaned_data['s_class']
                    rec.related_record = RecordData.objects.get(pk=form.cleaned_data['related_record'])
                    rec.record = form.cleaned_data['record']
                    rec.time = form.cleaned_data['time']
                    rec.visibility = form.cleaned_data['visibility']
                    rec.save()
                    return JsonResponse({'code': 1, 'message': '保存成功'})
                else:
                    return JsonResponse({'code': 0, 'message': '表单非法'})
            elif typename == 'delete':
                rec = _
                rec.delete()
                return JsonResponse({'code': 1, 'message': '删除成功'})
            else:
                return JsonResponse({'code': 0, 'message': '请求非法'})
        except Exception as e:
            print(e)
            return JsonResponse({'code': 0, 'message': '数据非法或发生了错误'})

    rec = _
    form = ModifyRecordHolderForm(classes,
                                  {'name': rec.name, 's_class': rec.s_class,
                                   'related_record': rec.related_record, 'record': rec.record,
                                   'time': rec.time, 'visibility': rec.visibility})

    return render(request, 'record/modify_record_holder.html', {'title': '修改纪录保持者 - %s' % rec.name, 'now_record_holder_manage': True,
                                                         'form': form,
                                                         'now_modify_record_holder': True,
                                                         'has_value': False
                                                         })