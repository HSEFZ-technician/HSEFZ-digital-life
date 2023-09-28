from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from volunteer.models import ScoreEventData, StudentScoreData
import json
from django.http import JsonResponse, Http404, HttpResponseRedirect
from volunteer.forms import ModifyScoreEventForm, SearchUserForm, ModifyScoreForm
from club.models import StudentClubData
from django.conf import settings
import datetime

# Create your views here.


def generate_row(name, score, date):
    template = '''
                    <tbody>
                    <tr>
                        <td class="name-content">
                            %s
                        </td>
                        <td class="snum-content">
                            %d
                        </td>
                        <td class="date-content">
                            %s
                        </td>
                    </tr>
                    </tbody>
    '''
    return template % (name, score, date)


@login_required()
def index(request):
    _ = StudentScoreData.objects.filter(user_id=request.user.pk)
    content = ''
    sum_of_course = 0
    for i in _:
        event = i.score_event_id
        sum_of_course += event.point
        content += generate_row(event.name, event.point, i.date_of_addition)
    return render(request, 'volunteer/home.html', {'content': content, 'percentage': (sum_of_course/40)*100, 'score': sum_of_course})


@login_required()
def score_manage(request):
    if (not request.user.is_superuser):
        raise Http404
    student_id = request.GET.get('id', None)
    modify_score_url = "/volunteer/modify_score"

    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode())
            typename = json_data['type']
            if typename == "new" and student_id != None:
                ev = ScoreEventData.objects.first()
                ss = StudentClubData.objects.get(pk=student_id)
                _ = StudentScoreData(
                    user_id=ss, score_event_id=ev, date_of_addition=datetime.datetime.now())
                _.save()
                return JsonResponse({'code': 1, 'message': '新建成功'})
            else:
                return JsonResponse({'code': 0, 'message': '请求非法'})
        except Exception as e:
            return JsonResponse({'code': 0, 'message': '数据非法或发生了错误'})

    table_div = ''
    user_data = ''

    if student_id != None:
        _s = StudentScoreData.objects.filter(user_id=student_id)
        ss = StudentClubData.objects.get(pk=student_id)
        user_data = ' - %s %s' % (ss.student_id, ss.student_real_name)
        table_content = "<tr><td><a href='%s?id=%d'>%s</a></td><td>%s</td><td>%s</td></tr>"
        cs = []
        for _ in _s:
            li = ScoreEventData.objects.filter(pk=_.score_event_id.pk)
            cs.append(table_content %
                      (modify_score_url, _.pk, li[0].name, li[0].point, _.date_of_addition))
        cs.sort(key=lambda x: x[0])

        for i in cs:
            table_div += i

    return render(request, 'volunteer/score_manage.html', {'title': '分数录入', 'now_score_manage': True, 'table_div': table_div, 'user_data': user_data})


@login_required()
def event_manage(request):

    if (not request.user.is_superuser):
        raise Http404

    modify_event_url = "/volunteer/modify_score_event"

    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode())
            typename = json_data['type']
            if typename == "new":
                _ = ScoreEventData(name='标题', point=0,
                                   user_id=request.user, desc='描述')
                _.save()
                return JsonResponse({'code': 1, 'message': '新建成功'})
            else:
                return JsonResponse({'code': 0, 'message': '请求非法'})
        except Exception as e:
            return JsonResponse({'code': 0, 'message': '数据非法或发生了错误'})

    _s = ScoreEventData.objects.all()
    table_content = "<tr><td><a href='%s?id=%d'>%s</a></td><td>%d</td></tr>"
    cs = []
    for _ in _s:
        cs.append(table_content %
                  (modify_event_url, _.pk, _.name, _.point))

    cs.sort(key=lambda x: x[0])

    table_div = ''

    for i in cs:
        table_div += i

    return render(request, 'volunteer/score_event_manage.html', {'title': '课时事件管理', 'now_score_event_manage': True, 'table_div': table_div})


@login_required()
def modify_score_event(request):

    score_event_id = request.GET.get('id', None)
    try:
        _ = ScoreEventData.objects.get(pk=score_event_id)
    except Exception as e:
        raise Http404

    cap = request.user.is_superuser

    if (not cap):
        raise Http404

    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode())
            typename = json_data['type']
            if typename == 'save':
                form = ModifyScoreEventForm({}, json_data['data'])
                rec = _
                if form.is_valid():
                    rec.name = form.cleaned_data['name']
                    rec.desc = form.cleaned_data['desc'].strip()
                    rec.point = form.cleaned_data['point']
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
            # print(e)
            return JsonResponse({'code': 0, 'message': '数据非法或发生了错误'})

    rec = _
    form = ModifyScoreEventForm(
        {'name': rec.name, 'desc': rec.desc, 'point': rec.point})

    return render(request, 'volunteer/modify_score_event.html', {'title': '修改课时事件 - %s' % rec.name, 'now_score_event_manage': True,
                                                                 'form': form,
                                                                 'now_modify_score_event': True,
                                                                 'has_value': True
                                                                 })


@login_required()
def search_user(request):
    cap = request.user.is_superuser

    if (not cap):
        raise Http404

    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode())
            typename = json_data['type']
            # print(json_data['data'])
            if typename == 'push':
                form = SearchUserForm({}, json_data['data'])
                if form.is_valid():
                    li = StudentClubData.objects.filter(
                        student_real_name=form.cleaned_data['name'], student_id=form.cleaned_data['class_id'])
                    if li.count() == 0:
                        return JsonResponse({'code': 0, 'message': '查无此人'})
                    return JsonResponse({'code': 1, 'message': '查询成功', 'id': li[0].pk})
                else:
                    return JsonResponse({'code': 0, 'message': '表单非法'})
            else:
                return JsonResponse({'code': 0, 'message': '请求非法'})
        except Exception as e:
            # print(e)
            return JsonResponse({'code': 0, 'message': '数据非法或发生了错误'})

    form = SearchUserForm(
        {'name': '', 'class_id': ''})

    return render(request, 'volunteer/search_user.html', {'title': '搜索用户', 'now_score_manage': False,
                                                          'form': form,
                                                          'now_search_user': True,
                                                          'has_value': True
                                                          })


@login_required()
def modify_score(request):

    score_id = request.GET.get('id', None)
    try:
        _ = StudentScoreData.objects.get(pk=score_id)
    except Exception as e:
        raise Http404

    user = StudentClubData.objects.get(pk=_.user_id.pk)

    cap = request.user.is_superuser
    types = [(i.pk, "%s - %d 课时" % (i.name, i.point))
             for i in ScoreEventData.objects.all()]

    if (not cap):
        raise Http404

    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode())
            typename = json_data['type']
            if typename == 'save':
                form = ModifyScoreForm(types, {}, json_data['data'])
                rec = _
                if form.is_valid():
                    rec.date_of_addition = form.cleaned_data['date']
                    rec.score_event_id = ScoreEventData.objects.get(
                        pk=form.cleaned_data['type_class'])
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
            # print(e)
            return JsonResponse({'code': 0, 'message': '数据非法或发生了错误'})

    rec = _
    form = ModifyScoreForm(types,
                           {'type_class': rec.score_event_id.pk, 'date': rec.date_of_addition})

    return render(request, 'volunteer/modify_score.html', {'title': '录入课时 - %s' % rec.user_id.student_real_name, 'now_score_manage': True,
                                                           'form': form,
                                                           'now_modify_score': True,
                                                           'has_value': True,
                                                           'user_data': '%s %s' % (user.student_id, user.student_real_name),
                                                           'user_id_score_input': _.user_id.pk
                                                           })
