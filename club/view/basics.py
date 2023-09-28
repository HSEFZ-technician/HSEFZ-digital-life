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

# Create your views here.


def home_view(request):
    return render(request, 'home.html', {'title': '华师二附中·数字生活'})


def logout_view(request):

    logout(request)

    return redirect('/')


def check_password(password):

    if re.fullmatch(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,30}$', password) == None:
        return False
    else:
        return True


def notice_view(request, id):
    try:
        _ = Notice.objects.get(pk=id)
        if (not _.active):
            raise Exception('Notice not active')
        return render(request, 'page.html', {'title': _.title, 'content': _.content})
    except Exception as e:
        raise Http404
