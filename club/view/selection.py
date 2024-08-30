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


def selection_home_view(request):

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

    user_groups = [t.name for t in request.user.groups.all()]
    required_groups = [t.name for t in _.student_group.all()]
    teacher_groups = [t.name for t in _.teachers_group.all()]

    avail = request.user.is_superuser

    for i in user_groups:
        for j in required_groups:
            if i == j:
                avail = True
        for j in teacher_groups:
            if i == j:
                avail = True

    if not avail:
        raise Http404

    res = get_selection_data(_, request.user, is_started)

    if request.method == 'POST':
        if (not is_started):
            return JsonResponse({'code': 0, 'message': '当前选课还未开始', 'data': res})
        json_data = json.loads(request.body.decode())
        class_id = json_data['class_id']
        type_name = json_data['type']
        try:
            if type_name == 'register':
                for c in res['data']:
                    if c['id'] == class_id:
                        with transaction.atomic():
                            # StudentSelectionInformation.objects.raw(
                            #     "LOCK TABLES club_studentselectioninformation;")
                            if c['status'] == 0 and (c['mnum'] - StudentSelectionInformation.objects.filter(info_id=class_id).count() > 0):
                                sel = StudentSelectionInformation(info_id=EventClassInformation.objects.get(
                                    pk=class_id), user_id=request.user, locked=False)
                                # StudentSelectionInformation.objects.raw("LOCK TABLES club_studentselectioninformation")
                                sel.save()
                                # StudentSelectionInformation.objects.raw(
                                #     "UNLOCK TABLES;")
                                # return JsonResponse({'code': 1, 'message': '报名成功', 'data': get_selection_data(_, request.user, True)})
                            else:
                                # StudentSelectionInformation.objects.raw(
                                #     "UNLOCK TABLES;")
                                return JsonResponse({'code': 0, 'message': '您当前无法报名此课程', 'data': res})
                        return JsonResponse({'code': 1, 'message': '报名成功', 'data': get_selection_data(_, request.user, True)})
            elif type_name == 'cancel_register':
                for c in res['data']:
                    if c['id'] == class_id:
                        if c['status'] == 4:
                            with transaction.atomic():
                                sel = StudentSelectionInformation.objects.select_for_update().filter(
                                    info_id=EventClassInformation.objects.get(pk=class_id), user_id=request.user, locked=False)
                                if sel.count() == 0:
                                    return JsonResponse({'code': 0, 'message': '您当前无法取消报名此课程', 'data': res})
                                else:
                                    sel.delete()
                            return JsonResponse({'code': 1, 'message': '取消报名成功', 'data': get_selection_data(_, request.user, True)})
                        else:
                            return JsonResponse({'code': 0, 'message': '您当前无法取消报名此课程', 'data': res})
            else:
                raise Exception
        except Exception as e:
            return JsonResponse({'code': 0, 'message': '请求非法', 'data': res})
        return JsonResponse({'code': 0, 'message': '无法找到该课程', 'data': res})

    if get_type == 'json':
        return JsonResponse(res)

    content = convert_selection_data_to_html(res)

    return render(request, 'selection_sign_up.html', {'title': _.title, 'sign_up_table_content': content,
                                                      'display_type': res['display_type'], 'domain': get_current_site(request),
                                                      'selection_id': _.pk})


@login_required()
def selection_desc_view(request):
    try:
        cid = request.GET.get('id', None)
        eci = EventClassInformation.objects.get(pk=cid)
        if (not eci.hf_desc):
            raise Http404
        _ = eci.event_id
        user_groups = [t.name for t in request.user.groups.all()]
        required_groups = [t.name for t in _.student_group.all()]
        teacher_groups = [t.name for t in _.teachers_group.all()]

        avail = request.user.is_superuser

        for i in user_groups:
            for j in required_groups:
                if i == j:
                    avail = True
            for j in teacher_groups:
                if i == j:
                    avail = True

        if not avail:
            raise Http404
        return render(request, 'page.html', {'title': eci.name, 'content': eci.full_desc})
    except Exception as e:
        raise Http404
