from django.db import models
from club.models import Group, StudentClubData


# Create your models here.


# League Data

class LeagueData(models.Model):
    name = models.CharField(max_length=200, blank=True,
                            verbose_name="League Data")

    user_id = models.ForeignKey(
        StudentClubData, verbose_name="Creator Info", on_delete=models.CASCADE)

    point = models.FloatField()