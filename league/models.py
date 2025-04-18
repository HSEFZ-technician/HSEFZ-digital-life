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

    def toDict(self):

        d = {
            "name": self.name,
            "a_class": self.a_class.name,
            "b_class": self.b_class.name,
            "a_class_c": self.a_class.color,
            "b_class_c": self.b_class.color,
            "a_class_s": self.a_class.slogan,
            "b_class_s": self.b_class.slogan,
            "a_class_d": self.a_class.desc,
            "b_class_d": self.b_class.desc,
            "a_score": self.a_score,
            "b_score": self.b_score,
            "time": self.time,
            "isPastEvent": self.isPastEvent
        }

        return d


class SeasonData(models.Model):

    name = models.CharField(max_length=200, blank=True,
                            verbose_name="Season Name")

    startdate = models.DateField(blank=True, verbose_name="Season Start Date")
    
    enddate = models.DateField(verbose_name="Season Start Date")

