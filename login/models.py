from django.db import models

class User(models.Model):
    nid = models.CharField(max_length=20)
    passwd = models.CharField(max_length=20)

class LoginUser(models.Model):
    nid = models.CharField(max_length=20)
    lip = models.CharField(max_length=32)
    time = models.DateTimeField('Log in Time')
