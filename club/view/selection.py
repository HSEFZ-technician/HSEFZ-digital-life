# from club.models import *
# from django.http import JsonResponse
# from django.views.decorators.http import require_POST
# from django.views.decorators.csrf import csrf_exempt
# from club.models import UserFavorite, EventClassInformation, StudentClubData
# import json
# from django.shortcuts import render, redirect
# from club.forms import RegisterForm, LoginForm, ModifyNoticeForm, ManualActivateForm, ModifyPasswordForm, SendModifyPasswordEmailForm, SettingModifyPasswordForm, ModifyEventForm
# from django.contrib import messages
# from django.contrib.auth import authenticate, login, logout
# from club.models import StudentClubData, Notice, SelectionEvent, StudentSelectionInformation, EventClassInformation, EventClassType
# from django.conf import settings
# from club.tokens import VerifyToken, PasswordGenerator
# from club.tasks import send_email
# from django.contrib.sites.shortcuts import get_current_site
# from django.template.loader import render_to_string
# from django.utils.html import strip_tags
# from django.utils import timezone
# from django.http import JsonResponse, Http404
# from django.db import transaction
# import datetime
# import time
# from django.contrib.auth.decorators import login_required
# import json
# import re
# from club.core import get_selection_data, convert_selection_data_to_html, get_selection_list

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string

import json
import datetime
import time
import re

from club.models import (
    UserFavorite,
    EventClassInformation,
    StudentClubData,
    StudentSelectionInformation,
    SelectionEvent,
    Notice,
    EventClassType
)

from club.core import get_selection_data, convert_selection_data_to_html, get_selection_list
from club.forms import (
    RegisterForm,
    LoginForm,
    ModifyNoticeForm,
    ManualActivateForm,
    ModifyPasswordForm,
    SendModifyPasswordEmailForm,
    SettingModifyPasswordForm,
    ModifyEventForm
)
from club.tokens import VerifyToken, PasswordGenerator
from club.tasks import send_email




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
                            e = EventClassInformation.objects.select_for_update().get(pk=class_id)
                            cr = e.current_num
                            if c['status'] == 0 and cr < c['mnum']:
                                sel = StudentSelectionInformation(
                                    info_id=EventClassInformation.objects.get(pk=class_id), user_id=request.user, locked=False)
                                sel.save()
                                EventClassInformation.objects.filter(pk=class_id).update(current_num=(cr+1))
                            else:
                                return JsonResponse({'code': 0, 'message': '您当前无法报名此课程', 'data': res})
                        return JsonResponse({'code': 1, 'message': '报名成功', 'data': get_selection_data(_, request.user, True)})
            elif type_name == 'cancel_register':
                for c in res['data']:
                    if c['id'] == class_id:
                        if c['status'] == 4:
                            with transaction.atomic():
                                e = EventClassInformation.objects.select_for_update().get(pk=class_id)
                                cr = e.current_num
                                sel = StudentSelectionInformation.objects.select_for_update().filter(
                                    info_id=EventClassInformation.objects.get(pk=class_id), user_id=request.user, locked=False)
                                if sel.count() == 0:
                                    return JsonResponse({'code': 0, 'message': '您当前无法取消报名此课程', 'data': res})
                                else:
                                    sel.delete()
                                    EventClassInformation.objects.filter(pk=class_id).update(current_num=(cr-1))
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


@require_POST
@login_required
def toggle_favorite(request):
    """
    处理报名/取消报名/收藏/取消收藏等操作
    前端通过 type 字段告诉后端要做哪种操作
    """
    user = request.user
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'code': 0, 'message': '数据格式错误'})

    action_type = data.get('type')
    class_id = data.get('class_id')

    if not class_id or not action_type:
        return JsonResponse({'code': 0, 'message': '缺少 class_id 或 type'})

    try:
        event_class = EventClassInformation.objects.get(pk=class_id)
    except EventClassInformation.DoesNotExist:
        return JsonResponse({'code': 0, 'message': '班级不存在'})

    if action_type == 'add_favorite':
        # 注册收藏（加一条记录）
        fav, created = UserFavorite.objects.get_or_create(
            user=user,
            event_class=event_class
        )
        if created:
            return JsonResponse({'code': 1, 'message': '已收藏'})
        else:
            return JsonResponse({'code': 1, 'message': '已存在收藏记录'})

    elif action_type == 'remove_favorite':
        # 取消收藏（删掉对应记录）
        deleted, _ = UserFavorite.objects.filter(
            user=user,
            event_class=event_class
        ).delete()
        if deleted:
            return JsonResponse({'code': 1, 'message': '已取消收藏'})
        else:
            return JsonResponse({'code': 0, 'message': '没有收藏记录可删除'})

    else:
        return JsonResponse({'code': 0, 'message': '未知操作类型'})