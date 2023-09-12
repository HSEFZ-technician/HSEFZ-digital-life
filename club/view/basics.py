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

# Create your views here.


def home_view(request):

    notice_template = '''<div class='row notice-row'><div class='notice-title'>
                         <a href='/notice/%d/'>%s</a></div><div class='notice-date'>
                         <span>%s</span></div></div>'''
    running_div = '''
        <div class="col-lg-6 selection">
        <div class="card selection-content">
            <div class="card-body">
              <h5 class="card-title">%s <span class="badge badge-pill badge-primary">进行中</span></h5>
              <h6 class="card-subtitle mb-2 text-muted">选课人群: %s</h6>
              <p class="card-text">选课时间为 %s 至 %s</p>
              <a href="%s" class="card-link">查看详情</a>
            </div>
        </div>
        </div>
    '''
    not_started_div = '''
    <div class="col-lg-6 selection">
        <div class="card selection-content">
            <div class="card-body">
              <h5 class="card-title">%s <span class="badge badge-pill badge-info">未开始</span></h5>
              <h6 class="card-subtitle mb-2 text-muted">选课人群: %s</h6>
              <p class="card-text">选课时间为 %s 至 %s</p>
              <a href="%s" class="card-link">查看详情</a>
            </div>
        </div>
        </div>
    '''

    notice_set = Notice.objects.filter(active=True)

    notice_div = ''

    selection_list = []

    selection_div = ''

    for n in notice_set:
        notice_div += notice_template % (n.id, n.title,
                                         n.release_date.strftime(settings.TIME_FORMAT))

    time_now = timezone.now()

    for s in SelectionEvent.objects.all():

        if s.end_time < time_now:

            continue

        student_string = ''

        student_count = s.student_group.count()

        if student_count == 0:
            student_string = '无'

        elif student_count == 1:
            student_string = s.student_group.all()[0].name

        else:
            student_string = s.student_group.all()[0].name + '等'

        if s.start_time <= time_now:

            selection_list.append((s.start_time, running_div % (s.title, student_string,
                                                                s.start_time.astimezone(settings.LOCAL_TIMEZONE).strftime(
                                                                    settings.SELECTION_TIME_FORMAT),
                                                                s.end_time.astimezone(settings.LOCAL_TIMEZONE).strftime(
                                                                    settings.SELECTION_TIME_FORMAT),
                                                                '/selection_sign_up/?id=%d' % (s.pk))))
        else:

            selection_list.append((s.start_time, not_started_div % (s.title, student_string,
                                                                    s.start_time.astimezone(settings.LOCAL_TIMEZONE).strftime(
                                                                        settings.SELECTION_TIME_FORMAT),
                                                                    s.end_time.astimezone(settings.LOCAL_TIMEZONE).strftime(
                                                                        settings.SELECTION_TIME_FORMAT),
                                                                    '/selection_sign_up/?id=%d' % (s.pk))))
    selection_list.sort(key=lambda x: x[0])

    for i in selection_list:

        selection_div += i[1]

    return render(request, 'selection_home.html', {'title': '华师二附中选课系统', 'notice_content': notice_div, 'selection_content': selection_div, 'hasClass': len(selection_list) != 0})


def logout_view(request):

    logout(request)

    return redirect('/')


def check_password(password):

    if re.fullmatch(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,30}$', password) == None:
        return False
    else:
        return True


def notice_view(request, id):
    try:
        _ = Notice.objects.get(pk=id)
        if (not _.active):
            raise Exception('Notice not active')
        return render(request, 'page.html', {'title': _.title, 'content': _.content})
    except Exception as e:
        raise Http404
