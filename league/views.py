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

    leagues = LeagueData.objects.all()
    form = []

    for m in leagues:

        i = m.toDict()

        date = i['start_time'].strftime('%Y-%m-%d')
        st = (i['start_time'] + datetime.timedelta(hours=8)).strftime("%H:%M")
        et = (i['end_time'] + datetime.timedelta(hours=8)).strftime("%H:%M")

        i['start_time'] = st
        i['end_time'] = et
        i['date'] = date
        form.append(i)

    return render(request, 'league/home.html', {'form': form})

# @login_required()
def sports_detail(request):
    # _ = StudentScoreData.objects.filter(user_id=request.user.pk)
    # content = ''
    # ck_table = StudentDataChecker.objects.filter(user_id=request.user.pk)
    # data_checked = False
    # if len(ck_table) != 0:
    #     data_checked = ck_table[0].data_checked
    # if request.method == 'POST':
    #     try:
    #         json_data = json.loads(request.body.decode())
    #         typename = json_data['type']
    #         if typename == "check":
    #             if len(ck_table) != 0:
    #                 ck_table[0].data_checked = True
    #                 ck_table[0].save()
    #             else:
    #                 tmp = StudentDataChecker(user_id=request.user.pk, data_checked=True)
    #                 # TODO： REFRESHING CHECKING DATA
    #                 tmp.save()
    #             return JsonResponse({'code': 1, 'message': '确认成功'})
    #         else:
    #             return JsonResponse({'code': 0, 'message': '请求非法'})
    #     except Exception as e:
    #         return JsonResponse({'code': 0, 'message': '发生了错误'})
    # sum_of_course = 0.0
    # for i in _:
    #     event = i.score_event_id
    #     sum_of_course += event.point
    #     content += generate_row(event.name, event.point, i.date_of_activity)
    # return render(request, 'league/sports_detail.html', {'content': content, 'percentage': (sum_of_course/40)*100, 'score': sum_of_course, 'checked': data_checked})
    return render(request, 'league/sports_detail.html')


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
                _ = LeagueData(title='赛事',
                               start_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                               end_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                               score_A=0, score_B=0,
                               team_A='team_A', team_B='team_B', visibility=1,
                               user_id=request.user)
                # _ = LeagueData(title='赛事', start_time=(datetime.datetime.now()+datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
                #                end_time=(datetime.datetime.now()+datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
                #                score_A=0, score_B=0,
                #                team_A='team_A', team_B='team_B', visibility=1,
                #                user_id=request.user)
                _.save()
                return JsonResponse({'code': 1, 'message': '新建成功'})
            else:
                return JsonResponse({'code': 0, 'message': '请求非法'})
        except Exception as e:
            return JsonResponse({'code': 0, 'message': '数据非法或发生了错误'})

    _s = LeagueData.objects.all()
    table_content = "<tr><td><a href='%s?id=%d'>%s</a></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%d</td><td>%d</td><td>%d</td></tr>"
    cs = []
    for _ in _s:
        cs.append(table_content %
                  (modify_event_url, _.pk, _.title,
                   (_.start_time + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
                   (_.end_time + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
                   _.team_A, _.team_B,
                   _.score_A, _.score_B, _.visibility))

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
                    rec.title = form.cleaned_data['title']
                    rec.start_time = form.cleaned_data['start_time']
                    rec.end_time = form.cleaned_data['end_time']
                    rec.score_A = form.cleaned_data['score_A']
                    rec.score_B = form.cleaned_data['score_B']
                    rec.team_A = form.cleaned_data['team_A']
                    rec.team_B = form.cleaned_data['team_B']
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
    form = ModifyLeagueForm(
        {'title': rec.title, 'start_time': rec.start_time,
         'end_time': rec.end_time,
         'score_A': rec.score_A, 'score_B': rec.score_B, 'team_A': rec.team_A, 'team_B': rec.team_B,
         'visibility': rec.visibility})

    return render(request, 'league/modify_league.html', {'title': '修改赛事 - %s' % rec.title, 'now_league_manage': True,
                                                                 'form': form,
                                                                 'now_modify_league': True,
                                                                 'has_value': True
                                                                 })

