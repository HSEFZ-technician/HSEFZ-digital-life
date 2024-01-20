import pandas as pd
import os
from club.tokens import *
# from club.models import *
import mysql.connector
from django.contrib.auth.hashers import make_password

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'club_main.settings')

# print(make_password(PasswordGenerator(20)))
print(make_password("111222m5"))
