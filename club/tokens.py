import jwt
from django.conf import settings
import random

class VerifyToken:

    @classmethod
    def token_generator(self, playload_data):
        return jwt.encode(
            playload_data,
            settings.JWT_SECRET_KEY,
            algorithm='HS256',  
        ).decode(encoding="utf-8")

    @classmethod
    def token_decode(self, token):
        data = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=['HS256',],
        )
        return data

def PasswordGenerator(length):

    new_password = ''

    for i in range(length-2):

        new_password += random.choice('0123456789abcdefghijklmnopqrstuvwxyz')

    new_password += random.choice('0123456789')

    new_password += random.choice('abcdefghijklmnopqrstuvwxyz')

    return new_password