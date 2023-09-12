from django.shortcuts import render, redirect
from club.forms import RegisterForm, LoginForm, ModifyNoticeForm, ManualActivateForm, ModifyPasswordForm, SendModifyPasswordEmailForm, SettingModifyPasswordForm, ModifyEventForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from club.models import StudentClubData, Notice, SelectionEvent, StudentSelectionInformation, EventClassInformation, EventClassType
from django.conf import settings
from club.tokens import VerifyToken, PasswordGenerator
from club.tasks import send_email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.http import JsonResponse, Http404
from django.db import transaction
import datetime
import time
from django.contrib.auth.decorators import login_required
import json
import re
from club.core import get_selection_data, convert_selection_data_to_html, get_selection_list


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

            student_id = register_form.cleaned_data['username']

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
            send_email.delay(mail_subject, message, [
                             student_username+settings.EMAIL_SUFFIX,])

            return render(request, 'info.html', {'info': '注册邮件已发送，请检查邮箱!'})

        else:
            return render(request, 'register.html', {'form': register_form, 'title': '注册'})

    else:
        form = RegisterForm()
        return render(request, 'register.html', {'form': form, 'title': '注册'})


def login_view(request, next="/"):

    try:

        if request.method == 'POST':
            login_form = LoginForm(request.POST)

            if login_form.is_valid():

                username = login_form.cleaned_data['email']

                password = login_form.cleaned_data['password']

                user = authenticate(username=username, password=password)

                if user is not None:

                    if (not user.is_created):
                        messages.error(request, "用户名或密码不匹配!")
                        return render(request, "login.html", {'form': login_form, 'title': '登录'})

                    if (not user.is_active):
                        messages.error(request, "该用户未激活邮箱!")
                        return render(request, "login.html", {'form': login_form, 'title': '登录'})

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
                    return render(request, "login.html", {'form': login_form, 'title': '登录'})

            else:
                return render(request, 'login.html', {'form': login_form, 'title': '登录'})

        else:
            form = LoginForm()
            next_url = request.GET.get('next', '/')
            return render(request, 'login.html', {'form': form, 'title': '登录', 'next_url': next_url})

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
            send_email.delay(mail_subject, message, [
                             account.username+settings.EMAIL_SUFFIX,])

            return render(request, 'info.html', {'info': '注册邮件已发送，请检查邮箱！'})

        else:
            return render(request, 'empty_form.html', {'form': manual_activate_form, 'title': '激活账号'})
    else:
        form = ManualActivateForm()
        return render(request, 'empty_form.html', {'form': form, 'title': '激活账号'})

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
    if request.method == 'POST':
        send_modify_password_email_form = SendModifyPasswordEmailForm(
            request.POST)
        if send_modify_password_email_form.is_valid():
            account_id = send_modify_password_email_form.cleaned_data['email']
            account = StudentClubData.objects.get(pk=account_id)

            new_password = PasswordGenerator(
                length=settings.NEW_PASSWORD_LENGTH)

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
            send_email.delay(mail_subject, message, [
                             account.username+settings.EMAIL_SUFFIX,])

            return render(request, 'info.html', {'info': '邮件已发送，请检查邮箱！'})
        else:
            return render(request, "empty_form.html", {'form': send_modify_password_email_form, 'title': '修改密码'})
    else:
        send_modify_password_email_form = SendModifyPasswordEmailForm()
        return render(request, "empty_form.html", {'form': send_modify_password_email_form, 'title': '修改密码'})
