from django.shortcuts import render, redirect
from django.http import HttpResponse
from club.tokens import *
from django.http import JsonResponse, Http404, HttpResponseRedirect
from youth_league.models import CourseData, CourseAssignmentScore, TestData, TestScore, AppealData, AppealDataTest
from youth_league.forms import *
from club.models import StudentClubData
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Avg
import json
from youth_league.core import *
from datetime import datetime

from django.contrib.auth.hashers import make_password

def generate_row(type, id, title, date, stu_score, avg, max, type1, id1, id2):
    template = '''
                    <tr>
                        <td id='%s-title-%s'>
                            %s
                        </td>
                        <td>
                            %s
                        </td>
                        <td>
                            %s
                        </td>
                        <td>
                            %s
                        </td>
                        <td>
                            %s
                        </td>
                        <td>
                            <button type='button' class='appeal-link btn btn-outline-secondary btn-sm' %s_id=%s data-toggle="modal" data-target="#appeal-window" onclick="showAppealWindow(%s);">申诉</button>
                        </td>
                    </tr>
    '''
    return template % (type, id, title,  date, stu_score, avg, max, type1, id1, id2)


def generate_row_notice(id, title, content, response, time):
    template = '''
                <div class="row entry-row">
                <div class="entry-title entry-category">
                    <a href="" data-toggle="modal" data-target="#appeal-window-%s">
                    申诉：%s
                    </a>
                </div>
                <div class="entry-date entry-category">
                    %s
                </div>
                </div>


                <div class="modal fade" id="appeal-window-%s" data-backdrop="static" data-keyboard="false" tabindex="-1" aria-labelledby="staticBackdropLabel" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable">
                    <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="staticBackdropLabel">申诉</h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        <h5>申诉内容：</h5>
                        %s
                        <hr>
                        <h5>申诉反馈:</h5>
                        %s
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-dismiss="modal">关闭</button>
                    </div>
                    </div>
                </div>
                </div>


                
    '''
    return template % (id, title, time, id, content, response)

@login_required()
def index(request):
    appeal_data_course = AppealData.objects.filter(stu_id=request.user.pk).values('id', 'content', 'response', 'update_time', 'creation_time', 'course_id').order_by('update_time')
    appeal_content = ''
    for i in appeal_data_course:
        course_title = CourseData.objects.filter(id=i['course_id']).values('title')[0]['title']
        if len(i['response']) != 0:
            appeal_content += generate_row_notice(i['id'], course_title, i['content'], i['response'], str(i['update_time'])[0:16])
        else:
            appeal_content += generate_row_notice(i['id'], course_title, i['content'], '暂无反馈', str(i['update_time'])[0:16])

    appeal_data_test = AppealDataTest.objects.filter(stu_id=request.user.pk).values('id', 'content', 'response', 'update_time', 'creation_time', 'test_id').order_by('update_time')
    for i in appeal_data_test:
        test_title = TestData.objects.filter(id=i['test_id']).values('title')[0]['title']
        if len(i['response']) != 0:
            appeal_content += generate_row_notice(i['id'], test_title, i['content'], i['response'], str(i['update_time'])[0:16])
        else:
            appeal_content += generate_row_notice(i['id'], test_title, i['content'], '暂无反馈', str(i['update_time'])[0:16])

    return render(request, 'youth_league/home.html', {'appeal_content': appeal_content})

@login_required()
def homework_inquiry(request):
    student_id = request.user.pk
    stu_score = CourseAssignmentScore.objects.filter(stu_id=student_id).values('score', 'course_id').order_by('course_id')
    stu_score_available = []
    stu_score_numc = 0
    for i in stu_score:
        stu_score_available.append(stu_score[stu_score_numc]['course_id'])
        stu_score_numc += 1

    course_list = CourseData.objects.all()
    content=''
    course_id_available_pointer=0
    for i in course_list:
        course_title = i.title
        course_date = i.date
        if i.pk in stu_score_available:
            course_stu_score = stu_score[course_id_available_pointer]['score']
            course_id_available_pointer += 1
        else:
            course_stu_score = '--'

        course_avg = CourseAssignmentScore.objects.filter(course_id=i.pk).aggregate(Avg('score'))['score__avg']
        course_max = CourseAssignmentScore.objects.filter(course_id=i.pk).aggregate(Max('score'))['score__max']
        content_type = 'course'
        content += generate_row(content_type, i.pk, course_title, course_date, course_stu_score, course_avg, course_max, content_type, i.pk, i.pk)

    if request.method == 'POST':
        form = getAppealContent(request.POST)
        if form.is_valid():
            course_id = form.cleaned_data.get('course_id')
            appeal_content = form.cleaned_data.get('appeal_content')
            appeal_entry = AppealData(stu_id = student_id, course_id = course_id, content=appeal_content, state=False)
            appeal_entry.save()
            return render(request, 'youth_league/appeal_submit_success.html', {'debug': ''})
    else:
        return render(request, 'youth_league/homework_inquiry.html', {'content': content, 'debug': '', 'course_list':course_list})


    return render(request, 'youth_league/homework_inquiry.html', {'content': content, 'debug': '', 'course_list':course_list})


@login_required()
def test_inquiry(request):
    student_id = request.user.pk
    stu_score = TestScore.objects.filter(stu_id=student_id).values('score', 'test_id').order_by('test_id')
    stu_score_available = []
    stu_score_numc = 0
    for i in stu_score:
        stu_score_available.append(stu_score[stu_score_numc]['test_id'])
        stu_score_numc += 1

    test_list = TestData.objects.all()
    content=''
    test_id_available_pointer=0
    for i in test_list:
        test_title = i.title
        test_date = i.date
        if i.pk in stu_score_available:
            test_stu_score = stu_score[test_id_available_pointer]['score']
            test_id_available_pointer += 1
        else:
            test_stu_score = '--'

        test_avg = TestScore.objects.filter(test_id=i.pk).aggregate(Avg('score'))['score__avg']
        test_max = TestScore.objects.filter(test_id=i.pk).aggregate(Max('score'))['score__max']
        content_type = 'test'
        content += generate_row(content_type, i.pk, test_title, test_date, test_stu_score, test_avg, test_max, content_type, i.pk, i.pk)

    if request.method == 'POST':
        form = getAppealContentTest(request.POST)
        if form.is_valid():
            test_id = form.cleaned_data.get('test_id')
            appeal_content = form.cleaned_data.get('appeal_content')
            appeal_entry = AppealDataTest(stu_id = student_id, test_id = test_id, content=appeal_content, state=False)
            appeal_entry.save()
            return render(request, 'youth_league/appeal_submit_success.html', {'debug': ''})
    else:
        return render(request, 'youth_league/test_inquiry.html', {'content': content, 'debug': '', 'test_list':test_list})

    return render(request, 'youth_league/test_inquiry.html', {'content': content, 'debug': form, 'test_list': test_list})


def course_manage(request):
    cap = request.user.is_superuser or request.user.is_staff
    if (not cap):
        raise Http404
    
    return render(request, 'youth_league/course_manage.html', {'now_course_manage': True})

def course_score_manage(request):
    cap = request.user.is_superuser or request.user.is_staff
    if (not cap):
        raise Http404
    
    return render(request, 'youth_league/course_score_manage.html', {'now_course_score_manage': True})

def test_manage(request):
    cap = request.user.is_superuser or request.user.is_staff
    if (not cap):
        raise Http404
    
    return render(request, 'youth_league/test_manage.html', {'now_test_manage': True})

def test_score_manage(request):
    cap = request.user.is_superuser or request.user.is_staff
    if (not cap):
        raise Http404
    
    return render(request, 'youth_league/test_score_manage.html', {'now_test_score_manage': True})



def generate_row_appeal_not_handled(appeal_id, stu_no, title, content, time):
    template = '''
                <button class="btn btn-outline-primary btn-block" type="button" data-toggle="collapse" data-target="#appeal-window-container-%s" aria-expanded="false" aria-controls="collapseExample">
                    申诉课程（考试）：%s
                    &nbsp; &nbsp; &nbsp;
                    申诉学生学号：%s
                    &nbsp; &nbsp; &nbsp;
                    申诉时间：%s
                </button>
                <div class="collapse" id="appeal-window-container-%s">
                <div class="card card-body">
                    <ul class="list-group list-group-flush">
                    申诉内容：
                    <li class="list-group-item">%s</li>
                    <br>
                    提交回复：
                    <li class="list-group-item">            
                        <input type="hidden" id="appeal-id" name="appeal_id">
                        <textarea class="form-control" id="appeal-respond-input-%s" name="appeal_respond_content" rows="10"></textarea>
                        <button class="btn btn-primary appeal-respond-submit" appeal_id="%s">提交</button>
                    </li>
                    </ul>
                </div>
                </div>
    '''
    return template % (appeal_id, title, stu_no, time, appeal_id, content, appeal_id, appeal_id)

def generate_row_appeal_handled(appeal_id, stu_no, title, content, time, response):
    template = '''
                <button class="btn btn-outline-secondary btn-block" type="button" data-toggle="collapse" data-target="#appeal-window-container-%s" aria-expanded="false" aria-controls="collapseExample">
                    申诉课程（考试）：%s
                    &nbsp; &nbsp; &nbsp;
                    申诉学生学号：%s
                    &nbsp; &nbsp; &nbsp;
                    申诉时间：%s
                </button>
                <div class="collapse" id="appeal-window-container-%s">
                <div class="card card-body">
                    <ul class="list-group list-group-flush">
                    申诉内容：
                    <li class="list-group-item">%s</li>
                    <br>
                    回复内容：
                    <li class="list-group-item">%s</li>
                    <br>
                    重新提交回复：
                    <li class="list-group-item">            
                        <input type="hidden" id="appeal-id" name="appeal_id">
                        <textarea class="form-control" id="appeal-respond-input-%s" name="appeal_respond_content" rows="10"></textarea>
                        <button class="btn btn-primary appeal-respond-submit" appeal_id="%s">提交</button>
                    </li>
                    </ul>
                </div>
                </div>
    '''
    return template % (appeal_id, title, stu_no, time, appeal_id, content, response, appeal_id, appeal_id)


def appeal_respond(request):
    cap = request.user.is_superuser or request.user.is_staff
    if (not cap):
        raise Http404

    appeal_data_not_handled = AppealData.objects.filter(state=False).values('id', 'stu_id', 'course_id', 'content', 'creation_time')
    appeal_data_handled = AppealData.objects.filter(state=True).values('id', 'stu_id', 'course_id', 'content', 'creation_time', 'response')
    content_not_handled = ''
    content_handled = ''
    for row in appeal_data_not_handled:
        appeal_id = row['id']
        stu_no = StudentClubData.objects.filter(id=row['stu_id']).values('student_id')[0]['student_id']
        course_title = CourseData.objects.filter(id=row['course_id']).values('title')[0]['title']
        content = row['content']
        creation_time = str(row['creation_time'])[0:16]
        content_not_handled += generate_row_appeal_not_handled(appeal_id, stu_no, course_title, content, creation_time)

    for row in appeal_data_handled:
        appeal_id = row['id']
        stu_no = StudentClubData.objects.filter(id=row['stu_id']).values('student_id')[0]['student_id']
        course_title = CourseData.objects.filter(id=row['course_id']).values('title')[0]['title']
        content = row['content']
        creation_time = str(row['creation_time'])[0:16]
        response = row['response']
        content_handled += generate_row_appeal_handled(appeal_id, stu_no, course_title, content, creation_time, response)

    if request.method == 'POST':
        form = getAppealRespond(request.POST)
        if form.is_valid():
            appeal_id = form.cleaned_data.get('appeal_id')
            appeal_respond_content = form.cleaned_data.get('appeal_respond_content')
            appeal_entry = AppealData.objects.filter(id=appeal_id)[0]
            appeal_entry.response = appeal_respond_content
            appeal_entry.update_time = datetime.now()
            appeal_entry.state = True
            appeal_entry.save()
    else:
        return render(request, 'youth_league/appeal_respond.html', {'now_appeal_respond': True, 'content_not_handled': content_not_handled, 'content_handled': content_handled})

    return render(request, 'youth_league/appeal_respond.html', {'now_appeal_respond': True, 'content_not_handled': content_not_handled, 'content_handled': content_handled})




def appeal_test_respond(request):
    cap = request.user.is_superuser or request.user.is_staff
    if (not cap):
        raise Http404

    appeal_data_not_handled = AppealDataTest.objects.filter(state=False).values('id', 'stu_id', 'test_id', 'content', 'creation_time')
    appeal_data_handled = AppealDataTest.objects.filter(state=True).values('id', 'stu_id', 'test_id', 'content', 'creation_time', 'response')
    content_not_handled = ''
    content_handled = ''
    for row in appeal_data_not_handled:
        appeal_id = row['id']
        stu_no = StudentClubData.objects.filter(id=row['stu_id']).values('student_id')[0]['student_id']
        test_title = TestData.objects.filter(id=row['test_id']).values('title')[0]['title']
        content = row['content']
        creation_time = str(row['creation_time'])[0:16]
        content_not_handled += generate_row_appeal_not_handled(appeal_id, stu_no, test_title, content, creation_time)

    for row in appeal_data_handled:
        appeal_id = row['id']
        stu_no = StudentClubData.objects.filter(id=row['stu_id']).values('student_id')[0]['student_id']
        test_title = TestData.objects.filter(id=row['test_id']).values('title')[0]['title']
        content = row['content']
        creation_time = str(row['creation_time'])[0:16]
        response = row['response']
        content_handled += generate_row_appeal_handled(appeal_id, stu_no, test_title, content, creation_time, response)

    if request.method == 'POST':
        form = getAppealRespond(request.POST)
        if form.is_valid():
            appeal_id = form.cleaned_data.get('appeal_id')
            appeal_respond_content = form.cleaned_data.get('appeal_respond_content')
            appeal_entry = AppealDataTest.objects.filter(id=appeal_id)[0]
            appeal_entry.response = appeal_respond_content
            appeal_entry.update_time = datetime.now()
            appeal_entry.state = True
            appeal_entry.save()
    else:
        return render(request, 'youth_league/appeal_test_respond.html', {'now_appeal_test_respond': True, 'content_not_handled': content_not_handled, 'content_handled': content_handled})

    return render(request, 'youth_league/appeal_test_respond.html', {'now_appeal_test_respond': True, 'content_not_handled': content_not_handled, 'content_handled': content_handled})