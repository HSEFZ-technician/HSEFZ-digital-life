from django.db import models
from club.models import Group, StudentClubData

# Create your models here.

class ClassTeamData(models.Model):

    name = models.CharField(max_length=200, blank=True,
                            verbose_name="Class Name")

    color = models.CharField(max_length=200, blank=True,
                        verbose_name="Class Color ID")
    
    slogan = models.CharField(max_length=500, blank=True, verbose_name="Class Slogan")
    
    desc = models.CharField(max_length=500, blank=True, verbose_name="Class Desc")

class MatchData(models.Model):

    name = models.CharField(max_length=200, blank=True,
                            verbose_name="Match Name")
    
    a_class = models.ForeignKey(
        ClassTeamData, verbose_name="A Competitor Info", on_delete=models.CASCADE, related_name='A_Class')
    
    b_class = models.ForeignKey(
        ClassTeamData, verbose_name="B Competitor Info", on_delete=models.CASCADE, related_name='B_Class')

    isPastEvent = models.BooleanField(default=False, verbose_name="Is A Past Event")
    
    a_score = models.IntegerField(blank=True, verbose_name="Class A Score")

    b_score = models.IntegerField(blank=True, verbose_name="Class B Score")
    
    time = models.DateTimeField(blank=True, verbose_name="Match Start Time")


class SeasonData(models.Model):

    name = models.CharField(max_length=200, blank=True,
                            verbose_name="Season Name")

    startdate = models.DateField(blank=True, verbose_name="Season Start Date")
    
    enddate = models.DateField(verbose_name="Season Start Date")

