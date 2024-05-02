import datetime

from crispy_forms.layout import HTML, ButtonHolder, Div, Field, Layout, Submit, Row, Column
from crispy_forms.bootstrap import AppendedText
from django import forms
from django.forms import widgets
from django.forms.widgets import PasswordInput
from crispy_forms.helper import FormHelper
from django.conf import settings
from league import colors

from . import models
from .models import MatchData, ClassTeamData
import re


# class ModifyLeagueForm(forms.Form):
#
#     name = forms.CharField(
#         label='事件标题',
#         required=True,
#         min_length=1,
#         max_length=30,
#     )
#
#     point = forms.FloatField(min_value=0, required=True, label='赛事')
#
#     def __init__(self, default_value, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.form_id = "id-setting_modify_league_form"
#         self.helper.form_method = 'post'
#
#         for k in default_value:
#             self.fields[k].initial = default_value[k]
#
#         self.helper.layout = Layout(
#             Field('name', css_class="form-control"),
#             Field('point', css_class="form-control"),
#         )
#
# class UploadFileForm(forms.Form):
#     file = forms.FileField()

class ModifyLeagueForm(forms.Form):

    name = forms.CharField(
        label='赛事名称',
        required=True,
        min_length=1,
        max_length=200
    )

    time = forms.DateTimeField(required=True, label='开始时间（格式：YYYY-mm-dd HH:mm:ss）')

    a_class = forms.ChoiceField(required=True, label='队伍A',
                                choices=ClassTeamData.objects.values_list("id", "name"))

    b_class = forms.ChoiceField(required=True, label='队伍B',
                                choices=ClassTeamData.objects.values_list("id", "name"))

    a_score = forms.IntegerField(required=True, label='队伍A分数')

    b_score = forms.IntegerField(required=True, label='队伍B分数')

    isPastEvent = forms.BooleanField(required=False, label='是否过时', initial=False)

    def __init__(self, query_set, default_value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-setting_modify_league_form"
        self.helper.form_method = 'post'
        self.fields['a_class'].choices = query_set
        self.fields['b_class'].choices = query_set

        for k in default_value:
            self.fields[k].initial = default_value[k]

        self.helper.layout = Layout(
            Field('name', css_class="form-control"),
            Field('time', css_class="form-control"),
            Field('a_class', css_class="form-control"),
            Field('b_class', css_class="form-control"),
            Field('a_score', css_class="form-control"),
            Field('b_score', css_class="form-control"),
            Field('isPastEvent', css_class="form-control"),
        )

    # def toBoolean(self, isPastEvent):
    #     if isPastEvent == 0:
    #         return True
    #     else:
    #         return False



class ModifyClassTeamForm(forms.Form):

    name = forms.CharField(
        label='班级名称',
        required=True,
        max_length=200,
    )

    color = forms.ChoiceField(required=True, label='班级颜色',
                              choices=colors.colors)

    slogan = forms.CharField(required=True, label='班级口号', max_length=500)

    desc = forms.CharField(required=True, label='班级介绍', max_length=500)

    def __init__(self, default_value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-setting_modify_class_team_form"
        self.helper.form_method = 'post'

        for k in default_value:
            self.fields[k].initial = default_value[k]

        self.helper.layout = Layout(
            Field('name', css_class="form-control"),
            Field('color', css_class="form-control"),
            Field('slogan', css_class="form-control"),
            Field('desc', css_class="form-control"),
        )


class UploadFileForm(forms.Form):
    file = forms.FileField()

