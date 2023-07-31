from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm, ManualActivateForm, ModifyPasswordForm, SendModifyPasswordEmailForm, SettingModifyPasswordForm, ModifyEventForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from .models import StudentClubData, Notice, SelectionEvent, StudentSelectionInformation, EventClassInformation, EventClassType
from django.conf import settings
from .tokens import VerifyToken, PasswordGenerator
from .tasks import send_email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.http import JsonResponse,Http404
import datetime
import time
from django.contrib.auth.decorators import login_required
import json
import re
from .core import get_selection_data, convert_selection_data_to_html, get_selection_list

# Create your views here.

def activate_email_view(request, token):

    try:
        data = VerifyToken.token_decode(token)
        account = StudentClubData.objects.get(pk=data['activate_id'])
    except Exception as e:
        return render(request, 'info.html', {'info': '询问非法或已过期'})

    if account is not None:
        account.is_active = True
        account.save()
        return render(request, 'info.html', {'info': '激活成功'})

    return render(request, "info.html", {'info': '账户不存在'})

def register_view(request):

    if request.method == 'POST':
        register_form = RegisterForm(request.POST)
        
        if register_form.is_valid():

            student_id       = register_form.cleaned_data['username']

            student_realname = register_form.cleaned_data['realname']

            student_username = register_form.cleaned_data['email']

            student_password = register_form.cleaned_data['password']

            new_account = StudentClubData.objects.filter(
                username=student_username
            )[0]

            new_account.set_password(student_password)

            new_account.is_created = True

            new_account.save()

            token = VerifyToken.token_generator(
                {
                    'activate_id': new_account.pk,
                    'username': student_username,
                    'sub': 'x'+str(int(time.time())),
                    'exp': datetime.datetime.utcnow()+datetime.timedelta(minutes=settings.EMAIL_EXPIRED_MINUTES),
                }
            )

            current_site = get_current_site(request)
            mail_subject = '激活你的账户'
            message = render_to_string(
                'email.html',
                {
                    'user': new_account,
                    'token': token,
                    'domain': current_site,
                    'title': '社团机选网站账号验证',
                    'information': '您好！您的账号正在进行邮箱验证，请点击下方链接完成邮箱认证，该邮件有效期'+str(settings.EMAIL_EXPIRED_MINUTES)+'分钟，请尽快完成验证！',
                    'is_activate': True,
                }
            )

            # print("start task")
            send_email.delay(mail_subject, message, [student_username+settings.EMAIL_SUFFIX,])

            return render(request,'info.html', {'info':'注册邮件已发送，请检查邮箱!'})
 
        else:
            return render(request,'register.html',{'form':register_form, 'title':'注册'})
    
    else:
        form = RegisterForm()
        return render(request,'register.html',{'form':form, 'title':'注册'})

def login_view(request, next="/"):

    try:

        if request.method == 'POST':
            login_form = LoginForm(request.POST)
            
            if login_form.is_valid():
                
                username = login_form.cleaned_data['email']

                password = login_form.cleaned_data['password']

                user     = authenticate(username=username,password=password)


                if user is not None:

                    if (not user.is_created):
                        messages.error(request,"用户名或密码不匹配1!")
                        return render(request,"login.html",{'form':login_form,'title':'登录'})

                    if (not user.is_active):
                        messages.error(request,"该用户未激活邮箱!")
                        return render(request,"login.html",{'form':login_form,'title':'登录'})

                    login(request, user)

                    if 'next_url' in request.POST:
                        next_url = request.POST['next_url']
                    else:
                        next_url = '/'

                    if next_url == '':
                        next_url = '/'

                    return redirect(next_url)

                else:

                    messages.error(request, "用户名或密码不匹配!")
                    return render(request,"login.html",{'form':login_form,'title':'登录'})

            else:
                return render(request,'login.html',{'form':login_form,'title':'登录'})
    
        else:
            form = LoginForm()
            next_url = request.GET.get('next','/')
            return render(request,'login.html',{'form':form, 'title':'登录', 'next_url': next_url})
        
    except Exception as e:
        print(e)
        raise Http404

def manual_activate_view(request):

    if request.method == 'POST':
        manual_activate_form = ManualActivateForm(request.POST)

        if manual_activate_form.is_valid():

            account_id = manual_activate_form.cleaned_data['email']

            account = StudentClubData.objects.get(pk=account_id)

            token = VerifyToken.token_generator(
                {
                    'activate_id': account.pk,
                    'username': account.username,
                    'sub': 'x'+str(int(time.time())),
                    'exp': datetime.datetime.utcnow()+datetime.timedelta(minutes=settings.EMAIL_EXPIRED_MINUTES),
                }
            )

            current_site = get_current_site(request)
            mail_subject = '激活你的账户'
            message = render_to_string(
                'email.html',
                {
                    'user': account,
                    'token': token,
                    'domain': current_site,
                    'title': '社团机选网站账号验证',
                    'information': '您好！您的账号正在进行邮箱验证，请点击下方链接完成邮箱认证，该邮件有效期'+str(settings.EMAIL_EXPIRED_MINUTES)+'分钟，请尽快完成验证！',
                    'is_activate': True,
                }
            )

            # print("start task")
            send_email.delay(mail_subject, message, [account.username+settings.EMAIL_SUFFIX,])

            return render(request, 'info.html',{'info':'注册邮件已发送，请检查邮箱！'})
        
        else:
            return render(request,'empty_form.html', {'form':manual_activate_form,'title':'激活账号'})
    else:
        form = ManualActivateForm()
        return render(request, 'empty_form.html', {'form':form, 'title':'激活账号'})

# def modify_password_view(request, token):

#     if request.method=='POST':
#         modify_password_form = ModifyPasswordForm(request.POST)

#         if modify_password_form.is_valid():
#             try:
#                 data = VerifyToken.token_decode(token)
#                 account = StudentClubData.objects.get(pk=data['password_id'])
#             except Exception as e:
#                 message.error(request, "地址非法!")
#                 return render(request,"empty_form.html",{'form':modify_password_form,'title':'修改密码'})
            
#             if account is not None:
#                 account.set_password(modify_password_form.cleaned_data['password'])
#                 account.save()

#                 return render(request, 'info.html', {'info':'新密码设置成功'})
#             else:
#                 message.error(request, "账户不存在!")
#                 return render(request,"empty_form.html",{'form':modify_password_form,'title':'修改密码'})
#         else:
#             return render(request,"empty_form.html",{'form':modify_password_form,'title':'修改密码'})
#     else:
#         modify_password_form=ModifyPasswordForm()
#         modify_password_form.set_action(token)
#         return render(request,"empty_form.html",{'form':modify_password_form,'title':'修改密码'})

def modify_password_view(request, token):

    try:

        data = VerifyToken.token_decode(token)
        account = StudentClubData.objects.get(pk=data['password_id'])
        new_password = data['new_password']
        account.set_password(new_password)
        account.save()

        return render(request, "info.html", {'info': '密码修改成功'})

    except Exception as e:
        return render(request, "info.html", {'info': '地址非法'})

# def send_modify_password_email_view(request):
#     if request.method=='POST':
#         send_modify_password_email_form=SendModifyPasswordEmailForm(request.POST)
#         if send_modify_password_email_form.is_valid():
#             account_id=send_modify_password_email_form.cleaned_data['email']
#             account = StudentClubData.objects.get(pk=account_id)

#             token = VerifyToken.token_generator(
#                 {
#                     'password_id': account.pk,
#                     'username': account.username,
#                     'sub': 'x'+str(int(time.time())),
#                     'exp': datetime.datetime.utcnow()+datetime.timedelta(minutes=settings.EMAIL_EXPIRED_MINUTES),
#                 }
#             )

#             current_site = get_current_site(request)
#             mail_subject = '修改你的密码'
#             message = render_to_string(
#                 'email.html',
#                 {
#                     'user': account,
#                     'token': token,
#                     'domain': current_site,
#                     'title': '社团机选网站账号密码修改',
#                     'information': '您好！您的账号正在进行密码修改，请点击下方链接并根据指示完成操作，该邮件有效期'+str(settings.EMAIL_EXPIRED_MINUTES)+'分钟，请尽快完成！',
#                     'is_activate': False,
#                 }
#             )

#             # print("start task")
#             send_email.delay(mail_subject, message, [account.username+settings.EMAIL_SUFFIX,])

#             return render(request, 'info.html',{'info':'邮件已发送，请检查邮箱！'})
#         else:
#             return render(request,"empty_form.html",{'form':send_modify_password_email_form,'title':'修改密码'})
#     else:
#         send_modify_password_email_form=SendModifyPasswordEmailForm()
#         return render(request,"empty_form.html",{'form':send_modify_password_email_form,'title':'修改密码'})


def send_modify_password_email_view(request):
    if request.method=='POST':
        send_modify_password_email_form=SendModifyPasswordEmailForm(request.POST)
        if send_modify_password_email_form.is_valid():
            account_id=send_modify_password_email_form.cleaned_data['email']
            account = StudentClubData.objects.get(pk=account_id)

            new_password = PasswordGenerator(length=settings.NEW_PASSWORD_LENGTH)

            token = VerifyToken.token_generator(
                {
                    'password_id': account.pk,
                    'username': account.username,
                    'new_password': new_password,
                    'sub': 'x'+str(int(time.time())),
                    'exp': datetime.datetime.utcnow()+datetime.timedelta(minutes=settings.EMAIL_EXPIRED_MINUTES),
                }
            )

            current_site = get_current_site(request)
            mail_subject = '修改你的密码'
            message = render_to_string(
                'email.html',
                {
                    'user': account,
                    'token': token,
                    'domain': current_site,
                    'title': '社团机选网站账号密码修改',
                    'information': '您好！您的账号正在进行密码修改，请点击下方链接，完成后密码将变为 %s，该邮件有效期' % (new_password)
                                    + str(settings.EMAIL_EXPIRED_MINUTES)+'分钟，请尽快完成！',
                    'is_activate': False,
                }
            )

            # print("start task")
            send_email.delay(mail_subject, message, [account.username+settings.EMAIL_SUFFIX,])

            return render(request, 'info.html',{'info':'邮件已发送，请检查邮箱！'})
        else:
            return render(request,"empty_form.html",{'form':send_modify_password_email_form,'title':'修改密码'})
    else:
        send_modify_password_email_form=SendModifyPasswordEmailForm()
        return render(request,"empty_form.html",{'form':send_modify_password_email_form,'title':'修改密码'})

def home_view(request):

    notice_template = '''<div class='row notice-row'><div class='notice-title'>
                         <a href='/notice/%d/'>%s</a></div><div class='notice-date'>
                         <span>%s</span></div></div>'''

    running_div     = '''
    <div class="col-lg-6 selection">
        <div class="selection-content border-running">
            <div class="home-selection-title title-running running-title"><font face="微软雅黑"><a href="%s" target="_blank">%s</a></font></div>
            <div class="row selection-info-content">
                <div class="selection-information">
                    <div class="selection-info-line"><span><font face="微软雅黑" style="font-weight:bold;color:#444;">选课人群:</font></span></div>
                    <div class="selection-info-line"><span><font face="微软雅黑" style="color:dimgrey;">%s</font></span></div>
                    <div class="button-container">
                        <button type="button" class="btn btn-info detail-button running-button" onclick="window.open('%s','_blank');">查看详情</button>
                    </div>
                </div>
                <div class="selection-status running-status">
                    <div class="selection-info-line">
                        <span><font face="微软雅黑" style="font-weight:bold;color:#444;">状态:</font></span>
                        <span class="ml-auto mr-auto"><font face="微软雅黑" style="font-weight:900;" class="running-text">进行中</font></span>
                    </div>
                    <div class="selection-info-line selection-hr-line"><hr class="running-hr"></div>
                    <div class="selection-info-line">
                        <span><font face="微软雅黑" style="font-weight:bold;color:#444;">时间:</font></span>
                        <span class="ml-auto" style="color: dimgrey;">%s</span>
                    </div>
                    <div class="selection-info-line" style="color: dimgrey;">
                        <span class="ml-auto"><font face="微软雅黑">至&nbsp;</font></span><span>%s</span>
                    </div>
                </div>
            </div>
        </div>
    </div>'''

    not_started_div = '''
    <div class="col-lg-6 selection">
        <div class="selection-content border-not-started">
            <div class="home-selection-title title-not-started not-started-title"><font face="微软雅黑"><a href="%s" target="_blank">%s</a></font></div>
            <div class="row selection-info-content">
                <div class="selection-information">
                    <div class="selection-info-line"><span><font face="微软雅黑" style="font-weight:bold;color:#444;">选课人群:</font></span></div>
                    <div class="selection-info-line"><span><font face="微软雅黑" style="color:dimgrey;">%s</font></span></div>
                    <div class="button-container">
                        <button type="button" class="btn btn-success detail-button not-started-button" onclick="window.open('%s','_blank');">查看详情</button>
                    </div>
                </div>
                <div class="selection-status not-started-status">
                    <div class="selection-info-line">
                        <span><font face="微软雅黑" style="font-weight:bold;color:#444;">状态:</font></span>
                        <span class="ml-auto mr-auto"><font face="微软雅黑" style="font-weight:900;" class="not-started-text">未开始</font></span>
                    </div>
                    <div class="selection-info-line selection-hr-line"><hr class="not-started-hr"></div>
                    <div class="selection-info-line">
                        <span><font face="微软雅黑" style="font-weight:bold;color:#444;">时间:</font></span>
                        <span class="ml-auto" style="color: dimgrey;">%s</span>
                    </div>
                    <div class="selection-info-line" style="color: dimgrey;">
                        <span class="ml-auto"><font face="微软雅黑">至&nbsp;</font></span><span>%s</span>
                    </div>
                </div>
            </div>
        </div>
    </div>'''

    notice_set      = Notice.objects.filter(active=True)

    notice_div      = ''

    selection_list  = []
    
    selection_div   = ''

    for n in notice_set:
        notice_div += notice_template % (n.id, n.title, n.release_date.strftime(settings.TIME_FORMAT))

    time_now        = timezone.now()

    for s in SelectionEvent.objects.all():

        if s.end_time < time_now:

            continue
        
        student_string = ''

        student_count  = s.student_group.count()

        if student_count == 0:
            student_string = '无'

        elif student_count == 1:
            student_string = s.student_group.all()[0].name

        else:
            student_string = s.student_group.all()[0].name + '等'
        
        if s.start_time <= time_now:

            selection_list.append((s.start_time, running_div     % ('/selection_sign_up/?id=%d' % (s.pk),
                                                                    s.title,
                                                                    student_string,
                                                                    '/selection_sign_up/?id=%d' % (s.pk),
                                                                    s.start_time.astimezone(settings.LOCAL_TIMEZONE).strftime(settings.SELECTION_TIME_FORMAT),
                                                                    s.end_time.astimezone(settings.LOCAL_TIMEZONE).strftime(settings.SELECTION_TIME_FORMAT))))
        else:

            selection_list.append((s.start_time, not_started_div % ('/selection_sign_up/?id=%d' % (s.pk),
                                                                    s.title,
                                                                    student_string,
                                                                    '/selection_sign_up/?id=%d' % (s.pk),
                                                                    s.start_time.astimezone(settings.LOCAL_TIMEZONE).strftime(settings.SELECTION_TIME_FORMAT),
                                                                    s.end_time.astimezone(settings.LOCAL_TIMEZONE).strftime(settings.SELECTION_TIME_FORMAT))))

    selection_list.sort(key=lambda x:x[0])

    for i in selection_list:

        selection_div += i[1]

    return render(request, 'home.html', {'title':'华师二附中选课系统', 'notice_content':notice_div, 'selection_content':selection_div})

def logout_view(request):

    logout(request)

    return redirect('/')


def check_password(password):

    if re.fullmatch(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,30}$',password) == None:
        return False
    else:
        return True


@login_required()
def selection_sign_up_view(request):

    get_type = request.GET.get('type', None)

    selection_id = request.GET.get('id', None)

    try:

        _ = SelectionEvent.objects.get(pk=selection_id)
    
    except Exception as e:

        raise Http404

    if _.end_time < timezone.now():
        raise Http404

    is_started = (_.start_time <= timezone.now())
    
    user_groups     = [t.name for t in request.user.groups.all()]
    required_groups = [t.name for t in _.student_group.all()]
    teacher_groups  = [t.name for t in _.teachers_group.all()]

    avail = request.user.is_superuser

    for i in user_groups:
        for j in required_groups:
            if i==j:
                avail = True
        for j in teacher_groups:
            if i==j:
                avail = True
    
    if not avail:
        raise Http404

    res     = get_selection_data(_, request.user, is_started)

    if request.method == 'POST':
        if (not is_started):
            return JsonResponse({'code':0,'message':'当前选课还未开始','data':res})
        try:
            json_data = json.loads(request.body.decode())
            class_id  = json_data['class_id']
            type_name = json_data['type']
            if type_name == 'register':
                for c in res['data']:
                    if c['id'] == class_id:
                        if c['status'] == 0:
                            sel = StudentSelectionInformation(info_id=EventClassInformation.objects.get(pk=class_id),user_id=request.user,locked=False)
                            sel.save()
                            return JsonResponse({'code':1,'message':'报名成功','data':get_selection_data(_, request.user, True)})
                        else:
                            return JsonResponse({'code':0,'message':'您当前无法报名此课程','data':res})
            elif type_name == 'cancel_register':
                for c in res['data']:
                    if c['id'] == class_id:
                        if c['status'] == 4:
                            sel = StudentSelectionInformation.objects.filter(info_id=EventClassInformation.objects.get(pk=class_id),user_id=request.user,locked=False)
                            if sel.count() == 0:
                                return JsonResponse({'code':0,'message':'您当前无法取消报名此课程','data':res})
                            else:
                                sel.delete()
                                return JsonResponse({'code':1,'message':'取消报名成功','data':get_selection_data(_, request.user, True)})
                        else:
                            return JsonResponse({'code':0,'message':'您当前无法取消报名此课程','data':res})
            else:
                raise Exception
        except Exception as e:
            return JsonResponse({'code':0,'message':'请求非法','data':res})
        return JsonResponse({'code':0,'message':'无法找到该课程','data':res})

    if get_type == 'json':
        return JsonResponse(res)
    
    content = convert_selection_data_to_html(res)
    
    return render(request, 'selection_sign_up.html', {'title': _.title, 'sign_up_table_content': content,
                                                      'display_type': res['display_type'], 'domain': get_current_site(request),
                                                      'selection_id': _.pk})

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
def selection_desc_view(request):
    try:
        cid = request.GET.get('id',None)
        eci = EventClassInformation.objects.get(pk=cid)
        if (not eci.hf_desc):
            raise Http404
        _   = eci.event_id
        user_groups     = [t.name for t in request.user.groups.all()]
        required_groups = [t.name for t in _.student_group.all()]
        teacher_groups  = [t.name for t in _.teachers_group.all()]

        avail = request.user.is_superuser

        for i in user_groups:
            for j in required_groups:
                if i==j:
                    avail = True
            for j in teacher_groups:
                if i==j:
                    avail = True
        
        if not avail:
            raise Http404
        return render(request,'page.html',{'title':eci.name,'content':eci.full_desc})
    except Exception as e:
        raise Http404

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
                    eci = EventClassInformation.objects.create(user_id=request.user,event_id=_,name='默认',desc='默认',max_num=0,full_desc='',class_type=EventClassType.objects.get(pk=types[0][0]),hf_desc=False,forbid_chs=False)
                    eci.save()
                    return JsonResponse({'code':1,'message':'创建成功','data':{
                                                                                'title':'默认',
                                                                                'short_desc':'默认',
                                                                                'max_num':0,
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

def page404(request,exception):
    return render(request,'info.html',{'info':'404 Not Found'})

def notice_view(request,id):
    try:
        _ = Notice.objects.get(pk=id)
        if (not _.active):
            raise Exception('Notice not active')
        return render(request,'page.html',{'title':_.title,'content':_.content})
    except Exception as e:
        raise Http404
