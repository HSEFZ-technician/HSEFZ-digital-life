from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.utils.translation import gettext_lazy as _
import django.contrib.auth.validators
from django.conf import settings

# Create your models here.


class StudentClubData(AbstractUser):

    first_name = ""
    last_name = ""

    email = models.EmailField(max_length=30, blank=False, verbose_name="student_email",
                              validators=[django.contrib.auth.validators.UnicodeUsernameValidator()])

    username = models.CharField(max_length=30, blank=False, verbose_name="student_email_name", unique=True,
                                validators=[django.contrib.auth.validators.UnicodeUsernameValidator()])

    student_id = models.CharField(max_length=20, blank=False, verbose_name="student_id",
                                  validators=[django.contrib.auth.validators.UnicodeUsernameValidator()])

    student_real_name = models.CharField(max_length=10, blank=False, verbose_name="student_real_name",
                                         validators=[django.contrib.auth.validators.UnicodeUsernameValidator()])

    is_created = models.BooleanField(verbose_name="Is This Account Created")


class SelectionEvent(models.Model):

    start_time = models.DateTimeField(verbose_name="start time")
    end_time = models.DateTimeField(verbose_name="end time")

    title = models.CharField(max_length=100, blank=False,
                             verbose_name="selection_title")

    student_group = models.ManyToManyField(Group, blank=True, verbose_name="Student Group Information",
                                           related_name="SelectionEvent_student_group")

    teachers_group = models.ManyToManyField(Group, blank=True, verbose_name="Teachers Group Information",
                                            related_name="SelectionEvent_teachers_group")


class EventClassType(models.Model):

    event_id = models.ForeignKey(
        SelectionEvent, verbose_name="Event Information", on_delete=models.CASCADE)

    type_name = models.CharField(
        max_length=30, blank=False, verbose_name="Class Type Name")


class EventClassTypeConstraints(models.Model):

    event_id = models.ForeignKey(
        SelectionEvent, verbose_name="Event Information", on_delete=models.CASCADE)

    type_id1 = models.ForeignKey(EventClassType, verbose_name="Type 1",
                                 on_delete=models.CASCADE, related_name="EventClassTypeConstraints_type_id1")

    coef_1 = models.IntegerField(verbose_name="Coefficient for type 1")

    type_id2 = models.ForeignKey(EventClassType, verbose_name="Type 2",
                                 on_delete=models.CASCADE, related_name="EventClassTypeConstraints_type_id2")

    coef_2 = models.IntegerField(verbose_name="Coefficient for type 2")

    C = models.IntegerField(verbose_name="Constant of the constraint")


class EventClassInformation(models.Model):

    event_id = models.ForeignKey(
        SelectionEvent, verbose_name="Event Information", on_delete=models.CASCADE)

    user_id = models.ForeignKey(
        StudentClubData, verbose_name="Teacher Information", on_delete=models.CASCADE)

    name = models.CharField(max_length=200, blank=True,
                            verbose_name="Class Name")

    desc = models.CharField(max_length=200, blank=True,
                            verbose_name="Class Description")

    max_num = models.IntegerField(
        verbose_name="Max Number of Students of the Class")

    current_num = models.IntegerField(
        verbose_name="Current Number of Students of the Class")

    full_desc = models.TextField(verbose_name="Class Full Description")

    class_type = models.ForeignKey(
        EventClassType, verbose_name="Class Type Information", on_delete=models.CASCADE)

    hf_desc = models.BooleanField(
        verbose_name="Whether Class Has Full Description")

    forbid_chs = models.BooleanField(verbose_name="Forbidden Status")


class StudentSelectionInformation(models.Model):

    info_id = models.ForeignKey(
        EventClassInformation, verbose_name="Class Information", on_delete=models.CASCADE)

    user_id = models.ForeignKey(
        StudentClubData, verbose_name="Student Information", on_delete=models.CASCADE)

    locked = models.BooleanField(verbose_name="Selection Locked Status")


class Notice(models.Model):

    title = models.CharField(max_length=50, blank=False,
                             verbose_name="Notice Title")

    release_date = models.DateField(verbose_name="Notice Release Data")

    content = models.TextField(verbose_name="Notice Content")

    active = models.BooleanField(verbose_name="Notice Status")
