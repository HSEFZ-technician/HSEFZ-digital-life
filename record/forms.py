import datetime

from crispy_forms.layout import HTML, ButtonHolder, Div, Field, Layout, Submit, Row, Column
from crispy_forms.bootstrap import AppendedText
from django import forms
from django.forms import widgets
from django.forms.widgets import PasswordInput
from crispy_forms.helper import FormHelper
from django.conf import settings

from .models import RecordData, RecordHolderData
import re


class ModifyRecordForm(forms.Form):

    name = forms.CharField(
        label='纪录名称',
        required=True,
        min_length=1,
        max_length=200
    )

    desc = forms.CharField(
        label='纪录简介',
        required=False,
        # min_length=1,
        max_length=500
    )

    type = forms.ChoiceField(required=True, label='纪录类型', choices=(("体育之最", "体育之最"), ("趣味之最", "趣味之最")))

    def __init__(self, default_value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-setting_modify_record_form"
        self.helper.form_method = 'post'
        self.fields['type'].choices = (("体育之最", "体育之最"), ("趣味之最", "趣味之最"))

        for k in default_value:
            self.fields[k].initial = default_value[k]

        self.helper.layout = Layout(
            Field('name', css_class="form-control"),
            Field('desc', css_class="form-control"),
            Field('type', css_class="form-control"),
        )


class ModifyRecordHolderForm(forms.Form):

    name = forms.CharField(label='纪录保持者', required=True, min_length=1, max_length=200)

    s_class = forms.CharField(label='班级', required=True, min_length=1, max_length=200)

    related_record = forms.ChoiceField(required=True, label='相关纪录',
                            choices=RecordData.objects.values_list("id", "name"))

    record = forms.CharField(label='纪录成绩', required=True, min_length=1, max_length=200)

    visibility = forms.BooleanField(required=False, label='可见性', initial=False)
    
    time = forms.DateTimeField(required=True, label='记录时间（格式：YYYY-mm-dd HH:mm:ss）')

    def __init__(self, query_set, default_value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-setting_modify_record_holder_form"
        self.helper.form_method = 'post'
        self.fields['related_record'].choices = query_set

        for k in default_value:
            self.fields[k].initial = default_value[k]

        self.helper.layout = Layout(
            Field('name', css_class="form-control"),
            Field('s_class', css_class="form-control"),
            Field('related_record', css_class="form-control"),
            Field('record', css_class="form-control"),
            Field('visibility', css_class="form-control"),
            Field('time', css_class="form-control")
        )