
import datetime
from django.db import models
# Create your models here.

class RecordData(models.Model):

    name = models.CharField(max_length=200, blank=True,
                            verbose_name="Record Name")

    desc = models.CharField(max_length=500, blank=True, verbose_name="Record Desc")

    type = models.CharField(max_length=200, default="体育之最", verbose_name="Record Type")

class RecordHolderData(models.Model):

    name = models.CharField(max_length=200, blank=True,
                            verbose_name="Student Name")
    
    s_class = models.CharField(max_length=200, blank=True,
                            verbose_name="Student Class")
    
    record = models.CharField(max_length=200, blank=True,
                            verbose_name="Record")

    related_record = models.ForeignKey(
        RecordData, verbose_name="Related Record", on_delete=models.CASCADE, related_name='record',
        blank=True, null=True)

    visibility = models.BooleanField(default=False, verbose_name="Visibility")

    time = models.DateTimeField(blank=True, verbose_name="Record Time",
                                default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))