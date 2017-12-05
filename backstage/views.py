# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, HttpResponse
from backstage.models import UserInfo, Status, Role
from werkzeug.security import generate_password_hash, check_password_hash
import time
import os
from django.http import JsonResponse

from django.conf import settings

# Create your views here.
def adduser(request):
    name, password, status, role = request.GET['name'], generate_password_hash(str(request.GET['password'])), request.GET['status'], request.GET['role']
    if UserInfo.objects.filter(name=name):
        return HttpResponse('user already exist')
    if not Status.objects.filter(id=status):
        return HttpResponse('status is not exist')
    if not Role.objects.filter(id=role):
        return HttpResponse('role is not exist')
    try:
        adddata = UserInfo(name=name, password=password, status_id=status, role_id=role)
        adddata.save()
    except Exception as e:
        return HttpResponse(e)
    return HttpResponse('adduser %s' % name)

def deluser(request):
    id = request.GET['id']
    try:
        UserInfo.objects.filter(id=id).delete()
    except Exception as e:
        return HttpResponse(e)
    return HttpResponse("OK!")

#使用Get请求
#def veruser(request):
#    name = request.GET['name']
#    password = str(request.GET['password'])
#    try:
#        data = UserInfo.objects.get(name=name)
#    except Exception:
#        return HttpResponse("%s is not exists" % name)
#    dpassword = data.password
#    if check_password_hash(dpassword, password):
#        return HttpResponse('true')
#    else:
#        return HttpResponse('false')

def veruser(request):
    name = request.POST.get('name')
    password = str(request.POST.get('password'))
    try:
        data = UserInfo.objects.get(name=name)
    except Exception:
        return HttpResponse("%s is not exists" % name)
    dpassword = data.password
    if check_password_hash(dpassword, password):
        return JsonResponse({'exec':'true'})
    else:
        return JsonResponse({'exec':'false'})


def chname(request):
    id = request.GET['id']
    name = request.GET['name']
    if UserInfo.objects.filter(name=name):
        return HttpResponse("%s already exists" % name)
    try:
        UserInfo.objects.filter(id=id).update(name=name)
    except Exception as e:
        return HttpResponse(e)
    return HttpResponse(True)

def chpasswd(request):
    id = request.GET['id']
    password = generate_password_hash(str(request.GET['password']))
    try:
        UserInfo.objects.filter(id=id).update(password=password)
    except Exception as e:
        return HttpResponse(e)
    return HttpResponse(True)

def chstatus(request):
    id = request.GET['id']
    status = request.GET['status']
    try:
        UserInfo.objects.filter(id=id).update(status=status)
    except Exception as e:
        return HttpResponse(e)
    return HttpResponse(True)

def chrole(request):
    id = request.GET['id']
    role = request.GET['role']
    try:
        UserInfo.objects.filter(id=id).update(role=role)
    except Exception as e:
        return HttpResponse(e)
    return HttpResponse(True)

def queryuser(request):
    #b = UserInfo.objects.values('name','password','status__ustatus','role__urole')
    #c = UserInfo.objects.filter(name='ssdx').values('name','password','status__ustatus','role__urole')
    try:
        name = request.GET['name']
        res = UserInfo.objects.filter(name=name).values('name','password','status__ustatus','role__urole')
    except Exception:
        res = UserInfo.objects.values('name','password','status__ustatus','role__urole')
    return HttpResponse(res)


def postfile(request):
    fname = request.FILES.get('file')
    dest=open(os.path.join(settings.FILE_UPLOAD_PATH, fname.name), 'wb+')
    for chunk in fname.chunks():
        dest.write(chunk)
    dest.close()
    return JsonResponse({'exec':'true'})

def delfile(request):
    fname = os.path.join(settings.FILE_UPLOAD_PATH, request.POST.get('file'))
    if os.path.exists(fname):
        os.remove(fname)
        return JsonResponse({'exec':'true'})
    else:
        return JsonResponse({'exec':'false'})

def listfile(request):
    fdict = []
    fname = os.listdir(settings.FILE_UPLOAD_PATH)
    for item in fname:
        fdict.append({'filename':item})
    return JsonResponse({'filelist':fdict})
