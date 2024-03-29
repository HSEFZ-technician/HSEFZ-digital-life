from crispy_forms.layout import HTML, ButtonHolder, Div, Field, Layout, Submit, Row, Column
from crispy_forms.bootstrap import AppendedText
from django import forms
from django.forms.widgets import PasswordInput
from crispy_forms.helper import FormHelper
from django.conf import settings
from .models import LeagueData
import re


class ModifyLeagueForm(forms.Form):

    name = forms.CharField(
        label='事件标题',
        required=True,
        min_length=1,
        max_length=30,
    )

    point = forms.FloatField(min_value=0, required=True, label='赛事')

    def __init__(self, default_value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-setting_modify_league_form"
        self.helper.form_method = 'post'

        for k in default_value:
            self.fields[k].initial = default_value[k]

        self.helper.layout = Layout(
            Field('name', css_class="form-control"),
            Field('point', css_class="form-control"),
        )

class UploadFileForm(forms.Form):
    file = forms.FileField()
