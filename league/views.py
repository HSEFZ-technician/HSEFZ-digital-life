from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from league.models import LeagueData
import json
from django.http import JsonResponse, Http404, HttpResponseRedirect
from league.forms import ModifyLeagueForm
from club.models import StudentClubData
from django.conf import settings
import datetime

# Create your views here.

def index(request):
    return render(request, 'league/home.html')

@login_required()
def league_manage(request):

    if (not (request.user.is_superuser or request.user.is_staff)):
        raise Http404

    modify_event_url = "/league/modify_league"

    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode())
            typename = json_data['type']
            if typename == "new":
                _ = LeagueData(name='标题', point=0,
                               user_id=request.user)
                _.save()
                return JsonResponse({'code': 1, 'message': '新建成功'})
            else:
                return JsonResponse({'code': 0, 'message': '请求非法'})
        except Exception as e:
            return JsonResponse({'code': 0, 'message': '数据非法或发生了错误'})

    _s = LeagueData.objects.all()
    table_content = "<tr><td><a href='%s?id=%d'>%s</a></td><td>%d</td></tr>"
    cs = []
    for _ in _s:
        cs.append(table_content %
                  (modify_event_url, _.pk, _.name, _.point))

    cs.sort(key=lambda x: x[0])

    table_div = ''

    for i in cs:
        table_div += i

    return render(request, 'league/league_manage.html', {'title': '赛事管理', 'now_league_manage': True, 'table_div': table_div})

@login_required()
def modify_league(request):

    score_event_id = request.GET.get('id', None)
    try:
        _ = LeagueData.objects.get(pk=score_event_id)
    except Exception as e:
        raise Http404

    cap = request.user.is_superuser or request.user.is_staff

    if (not cap):
        raise Http404

    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode())
            typename = json_data['type']
            if typename == 'save':
                form = ModifyLeagueForm({}, json_data['data'])
                rec = _
                if form.is_valid():
                    rec.name = form.cleaned_data['name']
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
    form = ModifyLeagueForm(
        {'name': rec.name, 'point': rec.point})

    return render(request, 'league/modify_league.html', {'title': '修改赛事 - %s' % rec.name, 'now_league_manage': True,
                                                                 'form': form,
                                                                 'now_modify_league': True,
                                                                 'has_value': True
                                                                 })

