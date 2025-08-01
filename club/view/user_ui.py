from django.shortcuts import render, redirect
from club.forms import RegisterForm, LoginForm, ModifyNoticeForm, ManualActivateForm, ModifyPasswordForm, SendModifyPasswordEmailForm, SettingModifyPasswordForm, ModifyEventForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from club.models import StudentClubData, Notice, SelectionEvent, StudentSelectionInformation, EventClassInformation, EventClassType
from django.conf import settings
from club.tokens import VerifyToken, PasswordGenerator
from club.tasks import send_email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.http import JsonResponse,Http404
from django.db import transaction
import datetime
import time
from django.contrib.auth.decorators import login_required
import json
import re
from club.core import get_selection_data, convert_selection_data_to_html, get_selection_list

def check_password(password):

    if re.fullmatch(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,30}$',password) == None:
        return False
    else:
        return True


@login_required()
def user_security_view(request):

    if request.method == 'POST':
        try:

            username = request.user.username
            # old_password = request.POST.get('old_password')
            # new_password = request.POST.get('new_password')

            # print(request.body.decode())

            json_data = json.loads(request.body.decode())
            old_password = json_data['old_password']
            new_password = json_data['new_password']

            if not check_password(new_password):
                data = {'code':0, 'message':'密码必须包含至少一个数字和字母'}
                return JsonResponse(data)

            user = authenticate(username = username, password = old_password)

            if user:

                user.set_password(new_password)
                user.save()

                data = {'code':1, 'message':'密码修改成功'}

                login(request, user)
            
            else:

                data = {'code':0, 'message':'原密码错误'}

            return JsonResponse(data)

        except Exception as e:

            # print(e)

            data = {'code':0,'message':'数据非法或发生了错误'}

            return JsonResponse(data)

    else:
        setting_modify_password_form = SettingModifyPasswordForm()
        return render(request, 'user_security.html', {'modify_password_form': setting_modify_password_form, 'title': '账号安全', 'now_user_security': True})


@login_required()
def user_info_view(request):
    
    # info_content = "%s %s %s %s"

    student_id        = request.user.student_id
    student_real_name = request.user.student_real_name
    student_email     = request.user.email

    student_groups    = ','.join([g.name for g in request.user.groups.all()])

    return render(request,'user_info.html',{'title':'个人信息','id': str(student_id),'real_name': str(student_real_name), 'email': str(student_email),'group': str(student_groups),'now_user_info': True})

@login_required()
def event_manage_view(request):

    if (not request.user.is_staff):
        raise Http404

    user_groups      = [t.name for t in request.user.groups.all()]
    _s               = SelectionEvent.objects.all()
    table_content    = "<tr><td><a href='%s?id=%d'>%s</a></td><td>%s</td><td>%s</td></tr>"
    modify_event_url = "/modify_event"
    cs               = []
    for _ in _s:
        teacher_groups  = [t.name for t in _.teachers_group.all()]
        cap = request.user.is_superuser
        for i in user_groups:
            for j in teacher_groups:
                if i == j:
                    cap = True
        if (not cap):
            continue
        cs.append((_.start_time,table_content % (modify_event_url, _.pk, _.title,
                                                 _.start_time.astimezone(settings.LOCAL_TIMEZONE).strftime(settings.SELECTION_TIME_FORMAT),
                                                 _.end_time.astimezone(settings.LOCAL_TIMEZONE).strftime(settings.SELECTION_TIME_FORMAT))))
    
    cs.sort(key=lambda x:x[0])

    table_div=''
    
    for i in cs:
        table_div+=i[1]

    return render(request,'event_manage.html',{'title':'课程管理','now_event_manage':True, 'table_div':table_div})

def comb_list_single_data(d):
    res=''
    for i in range(len(d)):
        res+='<tr><td>%d</td><td>%s</td><td><span>%s</span></td><td><span>%s</span></td></tr>' % (i+1,d[i]['n'],d[i]['e'],d[i]['g'])
    return res

@login_required()
def notice_manage_view(request):
    if (not request.user.is_superuser):
        raise Http404

    modify_notice_url = "/modify_notice"

    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode())
            typename  = json_data['type']
            if typename == "new":
                _ = Notice(release_date = datetime.datetime.now(), title = '标题', content = '', active = True)
                _.save()
                return JsonResponse({'code':1,'message':'新建成功'})
            else:
                return JsonResponse({'code':0,'message':'请求非法'})
        except Exception as e:
            # print(e)
            return JsonResponse({'code':0,'message':'数据非法或发生了错误'})

    _s               = Notice.objects.all()
    table_content    = "<tr><td><a href='%s?id=%d'>%s</a></td><td>%s</td></tr>"
    cs               = []
    for _ in _s:
        cs.append((_.release_date,table_content % (modify_notice_url, _.pk, _.title,
                                                 _.release_date)))
    
    cs.sort(key=lambda x:x[0])

    table_div=''
    
    for i in cs:
        table_div+=i[1]

    return render(request,'notice_manage.html',{'title':'公告管理','now_notice_manage':True, 'table_div':table_div})

@login_required()
def modify_notice_view(request):
    notice_id = request.GET.get('id',None)
    try:
        _ = Notice.objects.get(pk=notice_id)
    except Exception as e:
        raise Http404

    cap = request.user.is_superuser

    if (not cap):
        raise Http404

    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode())
            typename  = json_data['type']
            if typename == 'save':
                form = ModifyNoticeForm({},json_data['data'])
                rec = _
                if form.is_valid():
                    rec.title = form.cleaned_data['title']
                    rec.content = form.cleaned_data['content'].strip()
                    rec.save()
                    return JsonResponse({'code':1,'message':'保存成功'})
                else:
                    return JsonResponse({'code':0,'message':'表单非法'})
            elif typename == 'delete':
                rec = _
                rec.delete()
                return JsonResponse({'code':1,'message':'删除成功'})
            else:
                return JsonResponse({'code':0,'message':'请求非法'})
        except Exception as e:
            # print(e)
            return JsonResponse({'code':0,'message':'数据非法或发生了错误'})

    rec = _
    form = ModifyNoticeForm({'title':rec.title,'content':rec.content})
    return render(request,'modify_notice.html',{'title':'修改公告 - %s' % rec.title,
                                                'form':form,
                                                'now_modify_notice':True,
                                                'has_value':True
                                                })


@login_required()
def modify_event_view(request):

    event_id = request.GET.get('id',None)

    try:
        _ = SelectionEvent.objects.get(pk=event_id)
    except Exception as e:
        raise Http404

    types            = [(i.pk, i.type_name) for i in EventClassType.objects.filter(event_id=_)]    
    user_groups      = [t.name for t in request.user.groups.all()]
    teacher_groups   = [t.name for t in _.teachers_group.all()]
    student_groups   = [t.name for t in _.student_group.all()]
    cap = request.user.is_superuser

    for i in user_groups:
        for j in teacher_groups:
            if i == j:
                cap = True
    
    if (not cap):
        raise Http404

    if request.method == 'POST':
        if _.start_time <= timezone.now():
            return JsonResponse({'code':0,'message':'选课已开始，无法修改'})
        try:
            json_data = json.loads(request.body.decode())
            typename  = json_data['type']
            if typename == 'new':
                rec = EventClassInformation.objects.filter(user_id=request.user,event_id=_)
                if (rec.count() != 0):
                    return JsonResponse({'code':0,'message':'课程已存在，无法创建'})
                else:
                    eci = EventClassInformation.objects.create(user_id=request.user,event_id=_,name='默认',desc='默认',max_num=0,current_num=0,class_type=EventClassType.objects.get(pk=types[0][0]),hf_desc=False,forbid_chs=False)
                    eci.save()
                    return JsonResponse({'code':1,'message':'创建成功','data':{
                                                                                'title':'默认',
                                                                                'short_desc':'默认',
                                                                                'max_num':0,
                                                                                'current_num':0,
                                                                                'type_class':types[0][0],
                                                                                'linkToYearbook':'',
                                                                                'forbid_chosen':False,
                                                                            }})
            elif typename == 'delete':
                rec = EventClassInformation.objects.filter(user_id=request.user,event_id=_)
                if (rec.count() != 1):
                    return JsonResponse({'code':0,'message':'无法删除指定课程'})
                else:
                    rec[0].delete()
                    return JsonResponse({'code':1,'message':'课程删除成功'})
            elif typename == 'save':
                form = ModifyEventForm(types,{},json_data['data'])
                rec = EventClassInformation.objects.filter(user_id=request.user,event_id=_)
                if rec.count() == 0:
                    return JsonResponse({'code':0,'message':'指定课程不存在'})
                rec = rec[0]
                if form.is_valid():
                    rec.name = form.cleaned_data['title']
                    rec.desc = form.cleaned_data['short_desc']
                    rec.max_num = form.cleaned_data['max_num']
                    rec.current_num = 0
                    rec.full_desc = form.cleaned_data['linkToYearbook'].strip()
                    rec.hf_desc = (rec.full_desc != '')
                    rec.forbid_chs = form.cleaned_data['forbid_chosen']
                    rec.class_type = EventClassType.objects.get(pk=form.cleaned_data['type_class'])
                    rec.save()
                    return JsonResponse({'code':1,'message':'保存成功'})
                else:
                    return JsonResponse({'code':0,'message':'表单非法'})
            elif typename == 'add':
                rec = EventClassInformation.objects.filter(user_id=request.user,event_id=_)
                if rec.count() == 0:
                    return JsonResponse({'code':0,'message':'指定课程不存在'})
                rec = rec[0]
                mail = json_data['email']
                if (not mail.endswith(settings.EMAIL_SUFFIX)):
                    return JsonResponse({'code':0,'message':'该用户不存在'})
                user = StudentClubData.objects.filter(username=mail[:-len(settings.EMAIL_SUFFIX)])
                if user.count() == 0:
                    return JsonResponse({'code':0,'message':'该用户不存在'})
                user = user[0]
                ssi = StudentSelectionInformation.objects.filter(info_id=rec,user_id=user)
                if ssi.count() != 0:
                    return JsonResponse({'code':0,'message':'不能重复加入'})
                add_user_group = [g.name for g in user.groups.all()]
                cap = False
                for i in add_user_group:
                    for j in student_groups:
                        if i==j:
                            cap = True
                if (not cap):
                    return JsonResponse({'code':0,'message':'该用户不参加本次选课'})
                res = get_selection_data(_,user,True,ignore_forbid=True)
                cap = False
                for c in res['data']:
                    if c['id'] == rec.pk:
                        if c['status'] == 0:
                            cap = True
                        break
                if (not cap):
                    cc_l = [cc.info_id.name for cc in StudentSelectionInformation.objects.filter(user_id=user) if cc.info_id.event_id==_]
                    return JsonResponse({'code':0,'message':'该用户课程数已达上限或您设置的上限人数不够大，该用户已报名%s' % (','.join(cc_l))})

                ssi = StudentSelectionInformation(info_id=rec,user_id=user,locked=True)
                ssi.save()
                rec.current_num += 1
                rec.save()
                
                return JsonResponse({'code':1,'message':'添加成功','data':get_selection_list(rec)})
            elif typename == 'remove':
                rec = EventClassInformation.objects.filter(user_id=request.user,event_id=_)
                if rec.count() == 0:
                    return JsonResponse({'code':0,'message':'指定课程不存在'})
                rec = rec[0]
                mail = json_data['email']
                if (not mail.endswith(settings.EMAIL_SUFFIX)):
                    return JsonResponse({'code':0,'message':'该用户不存在'})
                user = StudentClubData.objects.filter(username=mail[:-len(settings.EMAIL_SUFFIX)])
                if user.count() == 0:
                    return JsonResponse({'code':0,'message':'该用户不存在'})
                user = user[0]
                ssi = StudentSelectionInformation.objects.filter(info_id=rec,user_id=user,locked=True)
                if ssi.count() == 0:
                    return JsonResponse({'code':0,'message':'记录不存在'})
                ssi = ssi[0]
                ssi.delete()
                rec.current_num -= 1
                rec.save()
                return JsonResponse({'code':1,'message':'删除成功','data':get_selection_list(rec)})

            else:
                return JsonResponse({'code':0,'message':'请求非法'})
        except Exception as e:
            # print(e)
            return JsonResponse({'code':0,'message':'数据非法或发生了错误'})

    rec = EventClassInformation.objects.filter(user_id=request.user,event_id=_)
    if rec.count() != 0:
        rec = rec[0]
        form = ModifyEventForm(types,{
                                        'title':rec.name,
                                        'short_desc':rec.desc,
                                        'max_num':rec.max_num,
                                        'type_class':rec.class_type.pk,
                                        'linkToYearbook':rec.full_desc,
                                        'forbid_chosen':rec.forbid_chs,
                                    })
        ld = get_selection_list(rec)
        return render(request,'modify_event.html',{'title':'修改课程',
                                                   'form':form,
                                                   'now_modify_event':True,
                                                   'has_value':True,
                                                   'locked_value':comb_list_single_data(ld['locked']),
                                                   'other_value':comb_list_single_data(ld['other'])
                                                   })
    else:
        form = ModifyEventForm(types,{})
        return render(request,'modify_event.html',{'title':'修改课程','form':form, 'now_modify_event': True,'has_value':False})
