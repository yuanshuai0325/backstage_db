# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

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
