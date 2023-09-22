from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from volunteer.models import ScoreEventData
import json
from django.http import JsonResponse, Http404
from volunteer.forms import ModifyScoreEventForm,SearchUserForm
from club.models import StudentClubData

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
    content = generate_row('111', 1, '2023/3/4')
    return render(request, 'volunteer/home.html', {'content': content, 'percentage': (25/40)*100, 'score': 25})


@login_required()
def score_manage(request):
    if (not request.user.is_superuser):
        raise Http404

    modify_score_url = "/volunteer/modify_score_data"

    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode())
            typename = json_data['type']
            if typename == "new":

                return JsonResponse({'code': 1, 'message': '新建成功'})
            else:
                return JsonResponse({'code': 0, 'message': '请求非法'})
        except Exception as e:
            return JsonResponse({'code': 0, 'message': '数据非法或发生了错误'})

    _s = StudentClubData.objects.all()
    table_content = "<tr><td><a href='%s?id=%d'>%s</a></td><td>%s</td><td>%s</td></tr>"
    cs = []
    for _ in _s:
        cs.append(table_content %
                  (modify_score_url, _.pk, _.student_real_name, _.student_id, _.email))

    cs.sort(key=lambda x: x[0])

    table_div = ''

    for i in cs:
        table_div += i

    return render(request, 'volunteer/score_manage.html', {'title': '分数录入', 'now_score_manage': True, 'table_div': table_div})


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
            if typename == 'post':
                form = SearchUserForm({}, json_data['data'])
                rec = _
                if form.is_valid():
                    rec.name = form.cleaned_data['name']
                    rec.desc = form.cleaned_data['class_id']
                    
                    return JsonResponse({'code': 1, 'message': '搜索成功'})
                else:
                    return JsonResponse({'code': 0, 'message': '表单非法'})
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
