from crispy_forms.layout import HTML, ButtonHolder, Div, Field, Layout, Submit, Row, Column
from crispy_forms.bootstrap import AppendedText
from django import forms
from django.forms.widgets import PasswordInput
from crispy_forms.helper import FormHelper
from django.conf import settings
from .models import StudentClubData
import re

class RegisterForm(forms.Form):
    username = forms.CharField(
        label      = '%d位学号'%(settings.STUDENT_ID_LENGTH),
        required   = True,
        min_length = settings.STUDENT_ID_LENGTH,
        max_length = settings.STUDENT_ID_LENGTH,
    )

    realname = forms.CharField(
        label      = '名字',
        required   = True,
        min_length = settings.REALNAME_MIN_LENGTH,
        max_length = settings.REALNAME_MAX_LENGTH,
    )

    email = forms.CharField(
        label      = '学校邮箱',
        required   = True,
        min_length = 1,
        max_length = 30,
    )

    password = forms.CharField(
        label      = '密码',
        widget     = forms.PasswordInput,
        required   = True,
        min_length = 8,
        max_length = 30,
    )

    password_confirm = forms.CharField(
        label      = '请再输入一遍',
        widget     = forms.PasswordInput,
        required   = True,
        min_length = 8,
        max_length = 30,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-register_form"
        self.helper.form_method = 'post'
        self.helper.form_action = '/register/'
        self.helper.form_show_labels = False

        self.helper.layout = Layout(
            Div(
                HTML('{% load static %}<img class="form-icon" src="{% static \'256x256.jpg\' %}" alt="校徽">'),
            ),
            HTML('<label class="input_hint">个人信息</label>'),
            Field('username', css_class="form-control item",
                placeholder='%d位学号'%(settings.STUDENT_ID_LENGTH)),
            Field('realname', css_class="form-control item",
                placeholder='名字'),
            AppendedText('email', settings.EMAIL_SUFFIX, css_class="form-control item", placeholder = '学校邮箱'),
            HTML('<label class="input_hint">密码</label>'),
            Field('password', css_class="form-control item",
                placeholder='密码'),
            Field('password_confirm', css_class="form-control item",
                placeholder='请再输入一遍'),

            ButtonHolder(
                Submit('submit', '注册', css_class="btn btn-block submit_button")
            ),
        )

    def clean_username(self):

        student_id_validator = r'^\d{'+str(settings.STUDENT_ID_LENGTH)+r'}$'

        value = self.cleaned_data['username']

        if re.fullmatch(student_id_validator, value) == None:
            raise forms.ValidationError('学号必须是%d位数字!'%(settings.STUDENT_ID_LENGTH), code='invalid')

        return value

    def clean_realname(self):

        realname_validator = r'^[\u4e00-\u9fa5]{' + str(settings.REALNAME_MIN_LENGTH) + r',' + str(settings.REALNAME_MAX_LENGTH) + r'}$'

        value = self.cleaned_data['realname']

        if re.fullmatch(realname_validator, value) == None:
            raise forms.ValidationError('姓名必须是%d~%d个汉字!'%(settings.REALNAME_MIN_LENGTH,settings.REALNAME_MAX_LENGTH), code='invalid')
        else:
            return value

    def clean_email(self):

        email_validator = r'^[A-Za-z._\d]+$'

        value = self.cleaned_data['email']

        if re.fullmatch(email_validator, value) == None:
            raise forms.ValidationError('邮箱只能包含大小写字母、.、下划线、数字!', code='invalid')
        
        try:
            student_id = self.cleaned_data['username']
            student_realname = self.cleaned_data['realname']
        except Exception as e:
            return value

        user = StudentClubData.objects.filter(username=value,student_id=student_id,student_real_name=student_realname)

        if user.count() == 0:
            raise forms.ValidationError('该学生不存在!', code='invalid')

        user=user[0]

        if user.is_created:
            raise forms.ValidationError('该用户已注册', code='invalid')
        
        return value

    def clean_password(self):

        password_validator = "^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,30}$"

        value = self.cleaned_data['password']

        if re.fullmatch(password_validator, value) == None:
            raise forms.ValidationError('密码必须包含一个字母和一个数字!', code='invalid')
        else:
            return value

    def clean_password_confirm(self):
        value = self.cleaned_data['password_confirm']

        try:
            target = self.cleaned_data['password']
        except Exception as e:
           return value
        else:
            if value != target or target is None:
                raise forms.ValidationError('密码不相同!', code='invalid')
            else:
                return value

class LoginForm(forms.Form):
    email    = forms.CharField(
        label      = '学校邮箱',
        required   = True,
        min_length = 1,
        max_length = 30,
    )

    password = forms.CharField(
        label      = '密码',
        widget     = forms.PasswordInput,
        required   = True,
        min_length = 6,
        max_length = 30,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-login_form"
        self.helper.form_method = 'post'
        self.helper.form_action = '/login/'
        self.helper.form_show_labels = False

        self.helper.layout = Layout(
            Div(
                HTML('{% load static %}<img class="form-icon" src="{% static \'256x256.jpg\' %}" alt="校徽">'),
            ),
            HTML('<input type="hidden" name="next_url" value="{{ next_url }}"/>'),
            HTML('<label class="input_hint">邮箱</label>'),
            AppendedText('email', settings.EMAIL_SUFFIX, css_class="form-control item", placeholder='学校邮箱'),
            HTML('<label class="input_hint">密码</label>'),
            Field('password', css_class="form-control item",
                placeholder='密码'),
            HTML('{% for message in messages %}\n<div {% if message.tags %} class ="{{ message.tags }}" {% endif %}><span class="password_or_username_invalid"><strong>{{ message }}</strong></span></div>\n{% endfor %}'),
            ButtonHolder(
                Submit('submit', '登录', css_class="btn btn-block submit_button")
            ),
        )
    
    def clean_email(self):

        email_validator = r'^[A-Za-z._\d]+$'

        value = self.cleaned_data['email']

        if re.fullmatch(email_validator, value) == None:
            raise forms.ValidationError('邮箱只能包含大小写字母、.、下划线、数字!', code='invalid')
        
        return value
    
    def clean_password(self):

        password_validator = "^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,30}$"

        value = self.cleaned_data['password']

        if re.fullmatch(password_validator, value) == None:
            raise forms.ValidationError('密码非法!', code='invalid')
        else:
            return value

class ManualActivateForm(forms.Form):
    email    = forms.CharField(
        label      = '学校邮箱',
        required   = True,
        min_length = 1,
        max_length = 30,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-manual_activate_form"
        self.helper.form_method = 'post'
        self.helper.form_action = '/manual_activate/'
        self.helper.form_show_labels = False

        self.helper.layout = Layout(
            Div(
                HTML('{% load static %}<img class="form-icon" src="{% static \'256x256.jpg\' %}" alt="校徽">'),
            ),
            HTML('<label class="input_hint">邮箱</label>'),
            AppendedText('email', settings.EMAIL_SUFFIX, css_class="form-control item", placeholder='学校邮箱'),
            HTML('{% for message in messages %}\n<div {% if message.tags %} class ="{{ message.tags }}" {% endif %}><span class="password_or_username_invalid"><strong>{{ message }}</strong></span></div>\n{% endfor %}'),
            ButtonHolder(
                Submit('submit', '发送激活邮件', css_class="btn btn-block submit_button")
            ),
        )
    
    def clean_email(self):

        email_validator = r'^[A-Za-z._\d]+$'

        value = self.cleaned_data['email']

        if re.fullmatch(email_validator, value) == None:
            raise forms.ValidationError('邮箱只能包含大小写字母、.、下划线、数字!', code='invalid')
        
        data=StudentClubData.objects.filter(username=value)

        if not data:
            raise forms.ValidationError('用户不存在!', code='invalid')
        
        if data[0].is_active:
            raise forms.ValidationError('用户已激活!', code='invalid')
        
        if (not data[0].is_created):
            raise forms.ValidationError('用户不存在!', code='invalid')

        return data[0].pk

class SendModifyPasswordEmailForm(forms.Form):
    email    = forms.CharField(
        label      = '学校邮箱',
        required   = True,
        min_length = 1,
        max_length = 30,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-send_modify_password_email"
        self.helper.form_method = 'post'
        self.helper.form_action = '/send_modify_password_email/'
        self.helper.form_show_labels = False

        self.helper.layout = Layout(
            Div(
                HTML('{% load static %}<img class="form-icon" src="{% static \'256x256.jpg\' %}" alt="校徽">'),
            ),
            HTML('<label class="input_hint">邮箱</label>'),
            AppendedText('email', settings.EMAIL_SUFFIX, css_class="form-control item", placeholder='学校邮箱'),
            HTML('{% for message in messages %}\n<div {% if message.tags %} class ="{{ message.tags }}" {% endif %}><span class="password_or_username_invalid"><strong>{{ message }}</strong></span></div>\n{% endfor %}'),
            ButtonHolder(
                Submit('submit', '发送密码修改邮件', css_class="btn btn-block submit_button")
            ),
        )
    
    def clean_email(self):

        email_validator = r'^[A-Za-z._\d]+$'

        value = self.cleaned_data['email']

        if re.fullmatch(email_validator, value) == None:
            raise forms.ValidationError('邮箱只能包含大小写字母、.、下划线、数字!', code='invalid')
        
        data=StudentClubData.objects.filter(username=value)

        if not data:
            raise forms.ValidationError('用户不存在!', code='invalid')
        
        if (not data[0].is_created):
            raise forms.ValidationError('用户不存在', code='invalid')

        return data[0].pk

class ModifyPasswordForm(forms.Form):

    password = forms.CharField(
        label      = '密码',
        widget     = forms.PasswordInput,
        required   = True,
        min_length = 8,
        max_length = 30,
    )

    password_confirm = forms.CharField(
        label      = '请再输入一遍',
        widget     = forms.PasswordInput,
        required   = True,
        min_length = 8,
        max_length = 30,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-modify_password_form"
        self.helper.form_method = 'post'
        # self.helper.form_action = '/modify_password/'
        self.helper.form_show_labels = False

        self.helper.layout = Layout(
            Div(
                HTML('{% load static %}<img class="form-icon" src="{% static \'256x256.jpg\' %}" alt="校徽">'),
            ),
            HTML('<label class="input_hint">新密码</label>'),
            Field('password', css_class="form-control item",
                placeholder='密码'),
            HTML('<label class="input_hint">确认密码</label>'),
            Field('password_confirm', css_class="form-control item",
                placeholder='请再输入一遍'),

            ButtonHolder(
                Submit('submit', '修改密码', css_class="btn btn-block submit_button")
            ),
        )

    def clean_password(self):

        password_validator = "^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,30}$"

        value = self.cleaned_data['password']

        if re.fullmatch(password_validator, value) == None:
            raise forms.ValidationError('密码必须包含一个字母和一个数字!', code='invalid')
        else:
            return value

    def clean_password_confirm(self):
        value = self.cleaned_data['password_confirm']

        try:
            target = self.cleaned_data['password']
        except Exception as e:
           return value
        else:
            if value != target or target is None:
                raise forms.ValidationError('密码不相同!', code='invalid')
            else:
                return value

    def set_action(self, token):
        self.helper.form_action='/modify_password/'+token+'/'

class SettingModifyPasswordForm(forms.Form):

    old_password = forms.CharField(
        label      = '旧密码',
        widget     = forms.PasswordInput,
        required   = True,
        min_length = 8,
        max_length = 30,
    )

    new_password = forms.CharField(
        label      = '新密码',
        widget     = forms.PasswordInput,
        required   = True,
        min_length = 8,
        max_length = 30,
    )

    password_confirm = forms.CharField(
        label      = '确认密码',
        widget     = forms.PasswordInput,
        required   = True,
        min_length = 8,
        max_length = 30,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-setting_modify_password_form"
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            Field('old_password', css_class="form-control"),
            Field('new_password', css_class="form-control"),
            Field('password_confirm', css_class="form-control"),
            HTML('<button class="btn btn-primary submit_button" type="submit" id="submit-id-submit">提交</button>'),
            # ButtonHolder(
            #     Submit('submit', '提交', css_class="btn btn-primary submit_button")
            # ),
        )

class ModifyEventForm(forms.Form):

    title = forms.CharField(
        label='课程标题',
        required=True,
        min_length=1,
        max_length=30,
    )

    short_desc = forms.CharField(
        label='课程短简介',
        required=True,
        min_length=1,
        max_length=100,
    )

    max_num = forms.IntegerField(
        label='最大人数',
        required=True,
        min_value=0,
        max_value=100000,
    )

    type_class = forms.ChoiceField(
        label='课程类型',
        choices=[(0,'default'),(1,'not_default')],
    )

    linkToYearbook = forms.CharField(
        label='社团年鉴网站地址',
        required=False,
        min_length=0,
        max_length=100,
    )

    forbid_chosen = forms.BooleanField(
        label='禁止其他人选课',
        required=False,
    )

    def __init__(self,query_set,default_value,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-setting_modify_event_form"
        self.helper.form_method = 'post'
        self.fields['type_class'].choices = query_set

        for k in default_value:
            self.fields[k].initial = default_value[k]

        self.helper.layout = Layout(
            Field('title', css_class="form-control"),
            Field('short_desc', css_class="form-control"),
            Field('max_num', css_class="form-control"),
            Field('type_class', css_class="form-control"),
            Field('linkToYearbook', css_class="form-control"),
            Field('forbid_chosen', css_class="form-control"),
        )