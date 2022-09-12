from club.models import *
import json
from django.conf import settings
from django.contrib.auth.models import Group
from club.tokens import PasswordGenerator

def add_user(json_path):
    with open(json_path,'r') as f:
        data = json.loads(f.read())['data']
    for i in data:
        scd = StudentClubData(email=i['mail'],username=i['mail'][:-len(settings.EMAIL_SUFFIX)],student_id=i['id'],student_real_name=i['name'], is_created = False, is_active = False, is_staff = False, is_superuser = False)
        scd.set_password(PasswordGenerator(20))
        scd.save()
        g = i['class']
        gs = Group.objects.filter(name=g)
        if gs.count() != 0:
            scd.groups.add(gs[0])
            scd.save()
        else:
            gs=Group(name=g)
            gs.save()
            scd.groups.add(gs)
            scd.save()