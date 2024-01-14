from django.db import models
from club.models import Group, StudentClubData
# Create your models here.


# Volunteer Data

class ScoreEventData(models.Model):

    name = models.CharField(max_length=200, blank=True,
                            verbose_name="Score Event Name")

    user_id = models.ForeignKey(
        StudentClubData, verbose_name="Creator Info", on_delete=models.CASCADE)

    point = models.FloatField()


class StudentScoreData(models.Model):

    user_id = models.ForeignKey(
        StudentClubData, verbose_name="Student Information", on_delete=models.CASCADE)

    score_event_id = models.ForeignKey(
        ScoreEventData, verbose_name="Score Event", on_delete=models.CASCADE)

    date_of_addition = models.DateField(verbose_name="Date Data")

    date_of_activity = models.CharField(
        max_length=200, verbose_name="Date Data", null=True)

    desc = models.CharField(
        max_length=200, verbose_name="Description", null=True)
    
class StudentDataChecker(models.Model):
    user_id = models.ForeignKey(
        StudentClubData, verbose_name="Student Information", on_delete=models.CASCADE)
    
    data_checked = models.BooleanField(verbose_name="Checked", default=False)