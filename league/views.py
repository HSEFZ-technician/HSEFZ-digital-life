from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from league import models, colors
from league.models import MatchData, ClassTeamData
import json
from django.http import JsonResponse, Http404, HttpResponseRedirect
from league.forms import ModifyLeagueForm, ModifyClassTeamForm
from club.models import StudentClubData
from django.conf import settings
import datetime


# Create your views here.

def index(request):
    matches = MatchData.objects.all()
    form = []

    for m in matches:
        pk = m.pk
        i = m.toDict()
        if i['isPastEvent']:
            continue
        time = (i['time'] + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
        i['time'] = time
        i['id'] = pk
        form.append(i)

    if len(form) == 0:
        return render(request, 'league/home.html', {'isEmpty': True})

    return render(request, 'league/home.html', {'form': form, 'title': 'EFZ数字生活·体育联赛'})


def detail(request):
    matches = MatchData.objects.all()
    form, form_past = [], []

    for m in matches:
        pk = m.pk
        i = m.toDict()
        time = (i['time'] + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
        i['time'] = time
        i['id'] = pk
        if i['isPastEvent']:
            form_past.append(i)
        else:
            form.append(i)

    if len(form) == 0 & len(form_past) == 0:
        return render(request, 'league/detail.html', {'isEmpty': True})

    return render(request, 'league/detail.html', {'form': form, 'form_past': form_past, 'title': '赛程详情'})


def sports_detail(request):
    matchID = request.GET.get('id', None)

    match = MatchData.objects.get(pk=matchID)
    i = match.toDict()
    time = (i['time'] + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
    i['time'] = time

    return render(request, 'league/sports_detail.html', {'league': i})


def match_map(request):
    return render(request, 'league/match_map.html')


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
                _ = MatchData(name='赛事', time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                              a_score=0, b_score=0,
                              a_class=ClassTeamData.objects.get(pk=1), b_class=ClassTeamData.objects.get(pk=1),
                              isPastEvent=False)
                _.save()
                return JsonResponse({'code': 1, 'message': '新建成功'})
            else:
                return JsonResponse({'code': 0, 'message': '请求非法'})
        except Exception as e:
            print(e)
            return JsonResponse({'code': 0, 'message': '数据非法或发生了错误'})

    _s = MatchData.objects.all()
    table_content = "<tr><td><a href='%s?id=%d'>%s</a></td><td>%s</td><td>%s</td><td>%s</td><td>%d</td><td>%d</td><td>%s</td></tr>"
    cs = []
    for _ in _s:
        cs.append(table_content %
                  (modify_event_url, _.pk, _.name,
                   (_.time + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
                   _.a_class.name, _.b_class.name,
                   _.a_score, _.b_score, _.isPastEvent))

    cs.sort(key=lambda x: x[0])

    table_div = ''

    for i in cs:
        table_div += i

    return render(request, 'league/league_manage.html',
                  {'title': '赛事管理', 'now_league_manage': True, 'table_div': table_div})


@login_required()
def class_team_manage(request):
    if (not (request.user.is_superuser or request.user.is_staff)):
        raise Http404

    modify_event_url = "/league/modify_class_team"

    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode())
            typename = json_data['type']
            if typename == "new":
                _ = ClassTeamData(name='class', color='1', slogan='slogan', desc='desc')
                _.save()
                return JsonResponse({'code': 1, 'message': '新建成功'})
            else:
                return JsonResponse({'code': 0, 'message': '请求非法'})
        except Exception as e:
            print(e)
            return JsonResponse({'code': 0, 'message': '数据非法或发生了错误'})

    _s = ClassTeamData.objects.all()
    table_content = "<tr><td><a href='%s?id=%d'>%s</a></td><td>%s</td><td>%s</td><td>%s</td></tr>"
    cs = []
    for _ in _s:
        cs.append(table_content %
                  (modify_event_url, _.pk, _.name, colors.colors[int(_.color) - 1][1],
                   # colors.colors[int(_.color) - 1][1] + ' ' + colors.colors_name[int(_.color) - 1],
                   _.slogan, _.desc))

    cs.sort(key=lambda x: x[0])

    table_div = ''

    for i in cs:
        table_div += i

    return render(request, 'league/class_team_manage.html',
                  {'title': '赛事管理', 'now_class_team_manage': True, 'table_div': table_div})


@login_required()
def create_league(request):
    cap = request.user.is_superuser or request.user.is_staff
    classes = [(i.pk, i.name)
               for i in ClassTeamData.objects.all()]

    if (not cap):
        raise Http404

    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode())
            typename = json_data['type']
            if typename == "new":
                form = ModifyLeagueForm(classes, {}, json_data['data'])
                print(form.data)
                if 'isPastEvent' in json_data['data']:
                    ISP = True
                else:
                    ISP = False
                _ = MatchData(name=form.data['name'],
                              time=datetime.datetime.strptime(form.data['time'], '%Y-%m-%d %H:%M:%S'),
                              a_score=form.data['a_score'],
                              b_score=form.data['b_score'],
                              a_class=ClassTeamData.objects.get(pk=form.data['a_class']),
                              b_class=ClassTeamData.objects.get(pk=form.data['b_class']),
                              isPastEvent=ISP)
                _.save()
                return JsonResponse({'code': 1, 'message': '新建成功'})
            else:
                return JsonResponse({'code': 0, 'message': '请求非法'})
        except Exception as e:
            print(e)
            return JsonResponse({'code': 0, 'message': '数据非法或发生了错误'})

    form = ModifyLeagueForm(classes, {})
    return render(request, 'league/create_league.html', {'title': '创建赛事', 'form': form})


@login_required()
def modify_league(request):
    score_event_id = request.GET.get('id', None)
    try:
        _ = MatchData.objects.get(pk=score_event_id)
    except Exception as e:
        raise Http404

    cap = request.user.is_superuser or request.user.is_staff
    classes = [(i.pk, i.name)
               for i in ClassTeamData.objects.all()]

    if (not cap):
        raise Http404

    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode())
            typename = json_data['type']
            if typename == 'save':
                form = ModifyLeagueForm(classes, {}, json_data['data'])
                rec = _
                if form.is_valid():
                    # print(form)
                    rec.name = form.cleaned_data['name']
                    rec.time = form.cleaned_data['time']
                    rec.a_score = form.cleaned_data['a_score']
                    rec.b_score = form.cleaned_data['b_score']
                    print(form.cleaned_data['a_class'])
                    print(ClassTeamData.objects.get(pk=form.cleaned_data['a_class']))
                    rec.a_class = ClassTeamData.objects.get(pk=form.cleaned_data['a_class'])
                    rec.b_class = ClassTeamData.objects.get(pk=form.cleaned_data['b_class'])
                    rec.isPastEvent = form.cleaned_data['isPastEvent']
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
    form = ModifyLeagueForm(classes,
                            {'name': rec.name, 'time': rec.time,
                             'a_score': rec.a_score, 'b_score': rec.b_score,
                             'a_class': rec.a_class, 'b_class': rec.b_class,
                             'isPastEvent': rec.isPastEvent})

    return render(request, 'league/modify_league.html', {'title': '修改赛事 - %s' % rec.name, 'now_league_manage': True,
                                                         'form': form,
                                                         'now_modify_league': True,
                                                         'has_value': False
                                                         })


@csrf_exempt
@login_required()
def modify_class_team(request):
    score_event_id = request.GET.get('id', None)
    try:
        _ = ClassTeamData.objects.get(pk=score_event_id)
    except Exception as e:
        raise Http404

    cap = request.user.is_superuser or request.user.is_staff
    # classes = [(i.pk, i.name)
    #            for i in ClassTeamData.objects.all()]

    if (not cap):
        raise Http404

    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode())
            typename = json_data['type']
            if typename == 'save':
                form = ModifyClassTeamForm({}, json_data['data'])
                rec = _
                if form.is_valid():
                    rec.name = form.cleaned_data['name']
                    rec.color = form.cleaned_data['color']
                    rec.slogan = form.cleaned_data['slogan']
                    rec.desc = form.cleaned_data['desc']
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
    form = ModifyClassTeamForm(
        {'name': rec.name, 'color': rec.color, 'slogan': rec.slogan, 'desc': rec.desc})

    return render(request, 'league/modify_class_team.html',
                  {'title': '修改班级 - %s' % rec.name, 'now_class_team_manage': True,
                   'form': form,
                   'now_modify_class_team': True,
                   'has_value': True
                   })

# @login_required()
# def sports_detail(request):
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
# return render(request, 'league/sports_detail.html')
