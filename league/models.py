from django.db import models
from club.models import Group, StudentClubData


# Create your models here.


# League Data

class LeagueData(models.Model):
    title = models.CharField(max_length=200, blank=True,
                            verbose_name="League Title")

    user_id = models.ForeignKey(
        StudentClubData, verbose_name="Creator Info", on_delete=models.CASCADE)

    start_time = models.DateTimeField(verbose_name="Start Time")

    end_time = models.DateTimeField(verbose_name="End Time")

    team_A = models.CharField(max_length=200, verbose_name="Team A")

    team_B = models.CharField(max_length=200, verbose_name="Team B")

    score_A = models.IntegerField(verbose_name="Score A")

    score_B = models.IntegerField(verbose_name="Score B")

    visibility = models.IntegerField(verbose_name="Visibility")

    def toDict(self):

        d = {
            "title": self.title,
            "user_id": self.user_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "team_A": self.team_A,
            "team_B": self.team_B,
            "score_A": self.score_A,
            "score_B": self.score_B,
            "visibility": self.visibility
        }

        # d['user_id'] = self.user_id
        # d['title'] = self.title
        # d['start_time'] = self.start_time
        # d['end_time'] = self.end_time
        # d['team_A'] = self.team_A
        # d['team_B'] = self.team_B
        # d['score_A'] = self.score_A
        # d['score_B'] = self.score_B
        # d['visibility'] = self.visibility

        return d

    # point = models.FloatField()