"""Regression tests for stored XSS in views that build HTML in Python.

Each test stores a value containing a script tag in a field that a
non-superuser (student, teacher, club manager or staff member) can set, renders
the page that displays it, and asserts the page shows the escaped form only.
"""
import datetime

import pytest
from django.contrib.auth.models import Group
from django.utils import timezone

from club.html_utils import join_html, safe_url
from club.models import (
    EventClassInformation,
    EventClassType,
    Notice,
    SelectionEvent,
    StudentClubData,
    StudentSelectionInformation,
)

PAYLOAD = '<script>alert(1)</script>'
ESCAPED = '&lt;script&gt;alert(1)&lt;/script&gt;'

pytestmark = pytest.mark.django_db


def assert_escaped(response, payload=PAYLOAD, escaped=ESCAPED):
    assert response.status_code == 200
    html = response.content.decode()
    assert payload not in html
    assert escaped in html


def make_user(username, **extra):
    defaults = dict(
        email=f'{username}@hsefz.cn',
        student_id='123456789',
        student_real_name='测试',
        is_created=True,
    )
    defaults.update(extra)
    return StudentClubData.objects.create_user(username=username, password='pw12345678', **defaults)


@pytest.fixture
def student(client):
    user = make_user('student')
    client.force_login(user)
    return user


@pytest.fixture
def staff(client):
    user = make_user('staff', is_staff=True)
    client.force_login(user)
    return user


@pytest.fixture
def selection(db):
    """A running selection event with a class whose fields hold XSS payloads."""
    students = Group.objects.create(name='students' + PAYLOAD)
    teachers = Group.objects.create(name='teachers')
    now = timezone.now()
    event = SelectionEvent.objects.create(
        title=PAYLOAD,
        start_time=now - datetime.timedelta(days=1),
        end_time=now + datetime.timedelta(days=1),
    )
    event.student_group.add(students)
    event.teachers_group.add(teachers)
    ctype = EventClassType.objects.create(event_id=event, type_name='type')
    manager = make_user('manager')
    manager.groups.add(teachers)
    eci = EventClassInformation.objects.create(
        event_id=event, user_id=manager, name=PAYLOAD, desc=PAYLOAD,
        max_num=10, current_num=0, class_type=ctype,
        full_desc='javascript:alert(1)', hf_desc=True, forbid_chs=False,
    )
    return {'event': event, 'class': eci, 'students': students,
            'teachers': teachers, 'manager': manager}


# --- helpers -----------------------------------------------------------------

def test_join_html_escapes_plain_strings():
    assert str(join_html([PAYLOAD])) == ESCAPED


@pytest.mark.parametrize('url,expected', [
    ('https://example.com/a', 'https://example.com/a'),
    ('/relative', '/relative'),
    ('javascript:alert(1)', '#'),
    (' JavaScript:alert(1)', '#'),
    ('java\tscript:alert(1)', '#'),
    ('data:text/html,x', '#'),
])
def test_safe_url(url, expected):
    assert safe_url(url) == expected


# --- club (selection system) -------------------------------------------------

def test_selection_home_escapes_titles_and_groups(client, selection):
    Notice.objects.create(title=PAYLOAD, release_date=datetime.date.today(),
                          content='', active=True)
    response = client.get('/selection/')
    assert_escaped(response)
    assert '<div class="card selection-content">' in response.content.decode()


def test_selection_sign_up_escapes_class_fields(client, student, selection):
    student.groups.add(selection['students'])
    response = client.get(f"/selection_sign_up/?id={selection['event'].pk}")
    assert_escaped(response)
    html = response.content.decode()
    # The club manager's "details" link must not become a javascript: URL.
    assert 'javascript:alert(1)' not in html
    # Markup built by the view is still real HTML, not double-escaped.
    assert "<button class='btn btn-primary sign-up'" in html
    assert "<a href='#' target='_blank'" in html


def test_selection_desc_escapes_full_desc(client, student, selection):
    student.groups.add(selection['students'])
    selection['class'].full_desc = PAYLOAD
    selection['class'].save()
    assert_escaped(client.get(f"/selection_desc/?id={selection['class'].pk}"))


def test_event_manage_escapes_event_title(client, selection):
    teacher = make_user('teacher', is_staff=True)
    teacher.groups.add(selection['teachers'])
    client.force_login(teacher)
    assert_escaped(client.get('/event_manage/'))


def test_modify_event_escapes_enrolled_student_names(client, selection):
    enrolled = make_user('enrolled', student_real_name='<b>x</b>')
    StudentSelectionInformation.objects.create(info_id=selection['class'], user_id=enrolled, locked=True)
    client.force_login(selection['manager'])
    response = client.get(f"/modify_event/?id={selection['event'].pk}")
    # Group name carries the main payload; student name a second one.
    assert_escaped(response)
    assert_escaped(response, '<b>x</b>', '&lt;b&gt;x&lt;/b&gt;')


def test_notice_manage_escapes_title(client):
    admin = make_user('admin', is_staff=True, is_superuser=True)
    client.force_login(admin)
    Notice.objects.create(title=PAYLOAD, release_date=datetime.date.today(), content='', active=True)
    assert_escaped(client.get('/notice_manage/'))


# --- youth league --------------------------------------------------------------

def test_appeal_respond_escapes_student_appeal(client, staff):
    from youth_league.models import AppealData, CourseData

    author = make_user('author')
    course = CourseData.objects.create(title='course' + PAYLOAD, date=datetime.date.today())
    AppealData.objects.create(stu_id=author.pk, course_id=course.pk, content=PAYLOAD, state=False)
    AppealData.objects.create(stu_id=author.pk, course_id=course.pk, content='c',
                              response='<img src=x onerror=alert(2)>', state=True)
    response = client.get('/youth_league/appeal_respond')
    assert_escaped(response)
    assert '<li class="list-group-item">' in response.content.decode()
    assert_escaped(response, '<img src=x onerror=alert(2)>', '&lt;img src=x onerror=alert(2)&gt;')


def test_appeal_test_respond_escapes_student_appeal(client, staff):
    from youth_league.models import AppealDataTest, TestData

    author = make_user('author')
    test = TestData.objects.create(title='test', date=datetime.date.today())
    AppealDataTest.objects.create(stu_id=author.pk, test_id=test.pk, content=PAYLOAD, state=False)
    assert_escaped(client.get('/youth_league/appeal_test_respond'))


def test_youth_league_home_escapes_appeal_and_response(client, student):
    from youth_league.models import AppealData, CourseData

    course = CourseData.objects.create(title=PAYLOAD, date=datetime.date.today())
    AppealData.objects.create(stu_id=student.pk, course_id=course.pk, content=PAYLOAD,
                              response=PAYLOAD, state=True)
    assert_escaped(client.get('/youth_league/'))


def test_homework_and_test_inquiry_escape_titles(client, student):
    from youth_league.models import CourseData, TestData

    CourseData.objects.create(title=PAYLOAD, date=datetime.date.today())
    TestData.objects.create(title=PAYLOAD, date=datetime.date.today())
    assert_escaped(client.get('/youth_league/homework_inquiry.html'))
    assert_escaped(client.get('/youth_league/test_inquiry.html'))


# --- volunteer -------------------------------------------------------------------

def test_volunteer_pages_escape_event_names(client, staff):
    from volunteer.models import ScoreEventData, StudentScoreData

    event = ScoreEventData.objects.create(name=PAYLOAD, point=1, user_id=staff)
    StudentScoreData.objects.create(user_id=staff, score_event_id=event,
                                    date_of_addition=datetime.date.today(), date_of_activity=PAYLOAD)
    assert_escaped(client.get('/volunteer/'))
    assert_escaped(client.get('/volunteer/score_event'))
    assert_escaped(client.get(f'/volunteer/score_input?id={staff.pk}'))


# --- league / record ----------------------------------------------------------------

def test_league_manage_pages_escape_names(client, staff):
    from league.models import ClassTeamData, MatchData

    team = ClassTeamData.objects.create(name=PAYLOAD, color='1', slogan=PAYLOAD, desc=PAYLOAD)
    MatchData.objects.create(name=PAYLOAD, a_class=team, b_class=team, a_score=0, b_score=0,
                             time=timezone.now())
    assert_escaped(client.get('/league/league_manage'))
    assert_escaped(client.get('/league/class_team_manage'))


def test_record_manage_pages_escape_names(client, staff):
    from record.models import RecordData, RecordHolderData

    record = RecordData.objects.create(name=PAYLOAD, desc=PAYLOAD)
    RecordHolderData.objects.create(name=PAYLOAD, s_class=PAYLOAD, record=PAYLOAD,
                                    related_record=record, time=timezone.now())
    assert_escaped(client.get('/record/record_manage'))
    assert_escaped(client.get('/record/record_holder_manage'))
