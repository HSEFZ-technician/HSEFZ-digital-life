from crispy_forms.layout import HTML, ButtonHolder, Div, Field, Layout, Submit, Row, Column
from crispy_forms.bootstrap import AppendedText
from django import forms
from django.forms.widgets import PasswordInput
from crispy_forms.helper import FormHelper
from django.conf import settings
import re

class getAppealContent(forms.Form):
    course_id = forms.CharField(label="course_id",)
    appeal_content = forms.CharField(label="appeal_content")

class getAppealContentTest(forms.Form):
    test_id = forms.CharField(label="test_id",)
    appeal_content = forms.CharField(label="appeal_content")

class UploadFileForm(forms.Form):
    file = forms.FileField()

class getAppealRespond(forms.Form):
    appeal_id = forms.CharField(label="appeal_id",)
    appeal_respond_content = forms.CharField(label="appeal_respond_content")