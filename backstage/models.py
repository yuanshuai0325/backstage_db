# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# 2017-12-22 token test
#from django.contrib.auth.models import User
#@receiver(post_save, sender=User)
#def create_auth_token(sender, instance=None, created=False, **kwargs):
#    if created:
#        Token.objects.create(user=instance)

# Create your models here.

class Status(models.Model):
    ustatus = models.CharField(max_length=20)

class Role(models.Model):
    urole = models.CharField(max_length=20)

class UserInfo(models.Model):
    name = models.CharField(max_length=30)
    password = models.CharField(max_length=100)
    status = models.ForeignKey('Status')
    role = models.ForeignKey('Role')

class Repo(models.Model):
    name = models.CharField(max_length=30)
    lpath = models.CharField(max_length=50)
    rpath = models.CharField(max_length=50)

class Project(models.Model):
    name = models.CharField(max_length=50)
    sname = models.CharField(max_length=30)
    repo = models.ForeignKey('Repo')

class Hosts(models.Model):
    host = models.CharField(max_length=50)
    repo = models.ForeignKey('Repo')

class Server(models.Model):
    name = models.CharField(max_length=30)
