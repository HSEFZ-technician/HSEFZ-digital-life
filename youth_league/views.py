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
from django.utils.html import format_html
from django.utils.safestring import mark_safe


# Course/test titles are set by staff and appeal content/responses are written
# by students and staff, so every generate_* helper escapes its arguments via
# format_html; the accumulated SafeStrings render with autoescaping on.

def generate_row(type, id, title, date, stu_score, avg, max, type1, id1, id2):
    template = '''
                    <tr>
                        <td id='{}-title-{}'>
                            {}
                        </td>
                        <td>
                            {}
                        </td>
                        <td>
                            {}
                        </td>
                        <td>
                            {}
                        </td>
                        <td>
                            {}
                        </td>
                        <td>
                            <button type='button' class='appeal-link btn btn-outline-secondary btn-sm' {}_id={} data-toggle="modal" data-target="#appeal-window" onclick="showAppealWindow({});">申诉</button>
                        </td>
                    </tr>
    '''
    return format_html(template, type, id, title,  date, stu_score, avg, max, type1, id1, id2)


def generate_row_notice(id, title, content, response, time):
    template = '''
                <div class="row entry-row">
                <div class="entry-title entry-category">
                    <a href="" data-toggle="modal" data-target="#appeal-window-{}">
                    申诉：{}
                    </a>
                </div>
                <div class="entry-date entry-category">
                    {}
                </div>
                </div>


                <div class="modal fade" id="appeal-window-{}" data-backdrop="static" data-keyboard="false" tabindex="-1" aria-labelledby="staticBackdropLabel" aria-hidden="true">
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
                        {}
                        <hr>
                        <h5>申诉反馈:</h5>
                        {}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-dismiss="modal">关闭</button>
                    </div>
                    </div>
                </div>
                </div>


                
    '''
    return format_html(template, id, title, time, id, content, response)

@login_required()
def index(request):
    appeal_data_course = AppealData.objects.filter(stu_id=request.user.pk).values('id', 'content', 'response', 'update_time', 'creation_time', 'course_id').order_by('update_time')
    appeal_content = mark_safe('')  # SafeString; += of format_html output stays safe
    # Load lookup tables once instead of querying per appeal row.
    course_titles = dict(CourseData.objects.values_list('id', 'title'))
    test_titles = dict(TestData.objects.values_list('id', 'title'))
    for i in appeal_data_course:
        course_title = course_titles.get(i['course_id'], '未知课程')
        if len(i['response']) != 0:
            appeal_content += generate_row_notice(i['id'], course_title, i['content'], i['response'], str(i['update_time'])[0:16])
        else:
            appeal_content += generate_row_notice(i['id'], course_title, i['content'], '暂无反馈', str(i['update_time'])[0:16])

    appeal_data_test = AppealDataTest.objects.filter(stu_id=request.user.pk).values('id', 'content', 'response', 'update_time', 'creation_time', 'test_id').order_by('update_time')
    for i in appeal_data_test:
        test_title = test_titles.get(i['test_id'])
        if len(i['response']) != 0:
            appeal_content += generate_row_notice(i['id'], test_title, i['content'], i['response'], str(i['update_time'])[0:16])
        else:
            appeal_content += generate_row_notice(i['id'], test_title, i['content'], '暂无反馈', str(i['update_time'])[0:16])

    return render(request, 'youth_league/home.html', {'appeal_content': appeal_content})

@login_required()
def homework_inquiry(request):
    student_id = request.user.pk
    # This student's scores keyed by course, fetched once.
    stu_score_map = dict(
        CourseAssignmentScore.objects.filter(stu_id=student_id)
        .values_list('course_id', 'score')
    )
    # Average and maximum per course computed in a single grouped query
    # instead of two aggregate queries per course.
    course_stats = {
        s['course_id']: s
        for s in CourseAssignmentScore.objects.values('course_id').annotate(
            avg=Avg('score'), max=Max('score'))
    }

    course_list = CourseData.objects.all()
    content = mark_safe('')  # SafeString; += of format_html output stays safe
    for i in course_list:
        course_title = i.title
        course_date = i.date
        course_stu_score = stu_score_map.get(i.pk, '--')

        stats = course_stats.get(i.pk, {})
        course_avg = stats.get('avg')
        course_max = stats.get('max')
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
    # This student's scores keyed by test, fetched once.
    stu_score_map = dict(
        TestScore.objects.filter(stu_id=student_id)
        .values_list('test_id', 'score')
    )
    # Average and maximum per test computed in a single grouped query
    # instead of two aggregate queries per test.
    test_stats = {
        s['test_id']: s
        for s in TestScore.objects.values('test_id').annotate(
            avg=Avg('score'), max=Max('score'))
    }

    test_list = TestData.objects.all()
    content = mark_safe('')  # SafeString; += of format_html output stays safe
    for i in test_list:
        test_title = i.title
        test_date = i.date
        test_stu_score = stu_score_map.get(i.pk, '--')

        stats = test_stats.get(i.pk, {})
        test_avg = stats.get('avg') if stats.get('avg') is not None else '--'
        test_max = stats.get('max') if stats.get('max') is not None else '--'
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
                <button class="btn btn-outline-primary btn-block" type="button" data-toggle="collapse" data-target="#appeal-window-container-{}" aria-expanded="false" aria-controls="collapseExample">
                    申诉课程（考试）：{}
                    &nbsp; &nbsp; &nbsp;
                    申诉学生学号：{}
                    &nbsp; &nbsp; &nbsp;
                    申诉时间：{}
                </button>
                <div class="collapse" id="appeal-window-container-{}">
                <div class="card card-body">
                    <ul class="list-group list-group-flush">
                    申诉内容：
                    <li class="list-group-item">{}</li>
                    <br>
                    提交回复：
                    <li class="list-group-item">            
                        <input type="hidden" id="appeal-id" name="appeal_id">
                        <textarea class="form-control" id="appeal-respond-input-{}" name="appeal_respond_content" rows="10"></textarea>
                        <button class="btn btn-primary appeal-respond-submit" appeal_id="{}">提交</button>
                    </li>
                    </ul>
                </div>
                </div>
    '''
    return format_html(template, appeal_id, title, stu_no, time, appeal_id, content, appeal_id, appeal_id)

def generate_row_appeal_handled(appeal_id, stu_no, title, content, time, response):
    template = '''
                <button class="btn btn-outline-secondary btn-block" type="button" data-toggle="collapse" data-target="#appeal-window-container-{}" aria-expanded="false" aria-controls="collapseExample">
                    申诉课程（考试）：{}
                    &nbsp; &nbsp; &nbsp;
                    申诉学生学号：{}
                    &nbsp; &nbsp; &nbsp;
                    申诉时间：{}
                </button>
                <div class="collapse" id="appeal-window-container-{}">
                <div class="card card-body">
                    <ul class="list-group list-group-flush">
                    申诉内容：
                    <li class="list-group-item">{}</li>
                    <br>
                    回复内容：
                    <li class="list-group-item">{}</li>
                    <br>
                    重新提交回复：
                    <li class="list-group-item">            
                        <input type="hidden" id="appeal-id" name="appeal_id">
                        <textarea class="form-control" id="appeal-respond-input-{}" name="appeal_respond_content" rows="10"></textarea>
                        <button class="btn btn-primary appeal-respond-submit" appeal_id="{}">提交</button>
                    </li>
                    </ul>
                </div>
                </div>
    '''
    return format_html(template, appeal_id, title, stu_no, time, appeal_id, content, response, appeal_id, appeal_id)


def appeal_respond(request):
    cap = request.user.is_superuser or request.user.is_staff
    if (not cap):
        raise Http404

    appeal_data_not_handled = AppealData.objects.filter(state=False).values('id', 'stu_id', 'course_id', 'content', 'creation_time')
    appeal_data_handled = AppealData.objects.filter(state=True).values('id', 'stu_id', 'course_id', 'content', 'creation_time', 'response')
    content_not_handled = mark_safe('')  # SafeString; += of format_html output stays safe
    content_handled = mark_safe('')  # SafeString; += of format_html output stays safe
    # Preload lookup tables once instead of querying per appeal row.
    stu_no_map = dict(StudentClubData.objects.values_list('id', 'student_id'))
    course_titles = dict(CourseData.objects.values_list('id', 'title'))
    for row in appeal_data_not_handled:
        appeal_id = row['id']
        stu_no = stu_no_map.get(row['stu_id'])
        course_title = course_titles.get(row['course_id'])
        content = row['content']
        creation_time = str(row['creation_time'])[0:16]
        content_not_handled += generate_row_appeal_not_handled(appeal_id, stu_no, course_title, content, creation_time)

    for row in appeal_data_handled:
        appeal_id = row['id']
        stu_no = stu_no_map.get(row['stu_id'])
        course_title = course_titles.get(row['course_id'])
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
    content_not_handled = mark_safe('')  # SafeString; += of format_html output stays safe
    content_handled = mark_safe('')  # SafeString; += of format_html output stays safe
    # Preload lookup tables once instead of querying per appeal row.
    stu_no_map = dict(StudentClubData.objects.values_list('id', 'student_id'))
    test_titles = dict(TestData.objects.values_list('id', 'title'))
    for row in appeal_data_not_handled:
        appeal_id = row['id']
        stu_no = stu_no_map.get(row['stu_id'])
        test_title = test_titles.get(row['test_id'])
        content = row['content']
        creation_time = str(row['creation_time'])[0:16]
        content_not_handled += generate_row_appeal_not_handled(appeal_id, stu_no, test_title, content, creation_time)

    for row in appeal_data_handled:
        appeal_id = row['id']
        stu_no = stu_no_map.get(row['stu_id'])
        test_title = test_titles.get(row['test_id'])
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