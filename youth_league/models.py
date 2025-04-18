from django.db import models
# Create your models here.


# Youth League Data

class CourseData(models.Model):

    title = models.CharField(max_length=200, blank=True,
                            verbose_name="Course Name")

    description = models.CharField(max_length=200, blank=True,
                            verbose_name="Course Description")
    
    creation_time = models.DateTimeField(auto_now=True)

    update_time = models.DateTimeField(auto_now=True)

    date = models.DateField(blank=True,
                            verbose_name="Course Date")



class CourseAssignmentScore(models.Model):

    stu_id = models.IntegerField()

    course_id = models.IntegerField(default=0)

    score = models.FloatField()

    creation_time = models.DateTimeField(auto_now=True)

    update_time = models.DateTimeField(auto_now=True)

class TestData(models.Model):

    title = models.CharField(max_length=200, blank=True,
                            verbose_name="Test Name")

    description = models.CharField(max_length=200, blank=True,
                            verbose_name="Test Description")
    
    creation_time = models.DateTimeField(auto_now=True)

    update_time = models.DateTimeField(auto_now=True)

    date = models.DateField(blank=True,
                            verbose_name="Test Date")

class TestScore(models.Model):

    stu_id = models.IntegerField()

    test_id = models.IntegerField(default=0)

    score = models.FloatField()

    creation_time = models.DateTimeField(auto_now=True)

    update_time = models.DateTimeField(auto_now=True)


class AppealData(models.Model):

    stu_id = models.IntegerField()

    course_id = models.IntegerField()

    content = models.TextField()

    response = models.TextField(blank=True)

    state = models.BooleanField()

    creation_time = models.DateTimeField(auto_now=True)

    update_time = models.DateTimeField(auto_now=True)

class AppealDataTest(models.Model):
    
    stu_id = models.IntegerField()

    test_id = models.IntegerField()

    content = models.TextField()

    response = models.TextField(blank=True)

    state = models.BooleanField()

    creation_time = models.DateTimeField(auto_now=True)

    update_time = models.DateTimeField(auto_now=True)

