# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, HttpResponse
from backstage.models import UserInfo, Status, Role
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import os
import time
import shutil
from django.http import JsonResponse

from django.conf import settings

from scripts.handledata import handledata, repo_map, repo_path, execcommand, host_map, short_name, execcmdrun

# 2017-12-22 token
#from rest_framework.authtoken.models import Token
#def create_auth_token(sender, instance=None, created=False, **kwargs):
#    if created:
#        Token.objects.create(user=instance)


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
    #print type(request.body) JSON数据传入为字符串
    print request.COOKIES.get('XToken')
    print request.COOKIES.get('expiretime')
    name = request.POST.get('name')
    password = str(request.POST.get('password'))
    try:
        data = UserInfo.objects.get(name=name)
    except Exception:
        reason = "用户 %s 不存在" % name
        return JsonResponse({'exec':'false', 'reason': reason})
    dpassword = data.password
    role = data.role.urole
    userid = data.id
    status = data.status.ustatus
    code = data.status.id
    print userid,status,code
    if check_password_hash(dpassword, password):
        if int(code) != 1:
            reason = "用户 %s 被禁用" % name
            return JsonResponse({'exec':'false', 'reason':reason})
        expiretime = time.time() + 1000
        XToken = jwt.encode({'name': name, 'userid' : userid, 'password' : dpassword, 'status' : status, 'code' : code, 'role' : role, 'expiretime': expiretime}, 'backstage_db', algorithm='HS256')
        return JsonResponse({'exec':'true', 'XToken':XToken})
    else:
        return JsonResponse({'exec':'false', 'reason':'用户密码错误'})

def userinfo(request):
    CXToken = request.COOKIES.get('XToken')
    XToken = jwt.decode(CXToken, 'backstage_db', 'HS256')
    name = XToken.get('name')
    userid = XToken.get('userid')
    dpassword = XToken.get('password')
    status = XToken.get('status')
    code = XToken.get('code')
    role = XToken.get('role')
    expiretime = XToken.get('expiretime')
    now = time.time()
    if expiretime - now < 0:
        return JsonResponse({'exec':'false', 'reason':'token超时,请重新登录'})
    try:
        data = UserInfo.objects.get(name=name)
    except Exception:
        return JsonResponse({'exec':'false', 'reason':'用户不存在'})
    if dpassword != data.password:
        return JsonResponse({'exec':'false', 'reason':'密码不正确'})
    elif int(code) != 1:
        return JsonResponse({'exec':'false', 'reason':'用户被禁用'}) 
    else:
        return JsonResponse({'exec':'true', 'username' : name, 'userid' : userid, 'status' : status, 'code' : code, 'role':[role]})

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
    userid = str(request.POST.get('userid'))
    opassword = str(request.POST.get('opassword'))
    cpassword = generate_password_hash(str(request.POST.get('cpassword')))
    print userid, opassword, cpassword
    try:
        password = UserInfo.objects.get(id=userid).password
    except Exception as e:
        return JsonResponse({'exec':'false', 'reason':'用户不存在'})
    if check_password_hash(password, opassword):
        print opassword
        try:
            UserInfo.objects.filter(id=userid).update(password=cpassword)
        except Exception as e:
            return JsonResponse({'exec':'false', 'reason':'密码修改失败'})
    else:
         return JsonResponse({'exec':'false', 'reason':'原密码错误'})
    return JsonResponse({'exec':'true'})

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

#def backupfile(request):
#    jarlist = request.POST.lists()[0][1]
#    rmap = []
#    dellist = []
#    repo_map = {
#        'as-gateway-web': 'asgw',
#        'as-interface-monitor':'asmsrv',
#        'as-service-monitor':'asmsrv',
#        'as-service-push':'asmsrv',
#        'rc-service-code':'code',
#        'rc-service-share':'code',
#        'bbs':'gw',
#        'rc-gateway-web':'gw',
#        'rc-service-common':'msrv',
#        'rc-service-file':'msrv',
#        'rc-service-monitor':'msrv',
#        'rc-service-msg':'msrv',
#        'rc-service-solr':'msrv',
#        'rc-service-user':'msrv',
#        'rc-service-ofs':'tmsrv',
#        'rc-service-itm':'tmsrv'
#    }
#    repo_path = {
#        'asgw': '/repo/tongren/asgw',
#        'asmsrv': '/repo/tongren/asmsrv',
#        'code': '/repo/tongren/code',
#        'gw': '/repo/tongren/gw',
#        'msrv': '/repo/tongren/msrv',
#        'tmsrv': '/repo/tongren/tmsrv',
#    }
#    for item in jarlist:
#        temp = item.replace('-0.0.1-SNAPSHOT.jar', '').replace('.jar', '')
#        print temp
#        if repo_map.get(temp):
#            rmap.append(repo_map.get(temp))
#        else:
#            dellist.append(item)
#            jarlist.remove(item)
#    rmap = set(rmap)
#    for item in rmap:
#        shutil.copytree(os.path.join(repo_path.get(item), 'lastest'), os.path.join(repo_path.get(item), time.strftime('%Y%m%d%H%M%S')))
#    for item in jarlist:
#        temp = item.replace('-0.0.1-SNAPSHOT.jar', '').replace('.jar', '')
#        shutil.copyfile(os.path.join('/fupload/lastest/', item), os.path.join(repo_path.get(repo_map.get(temp)), 'lastest/'+item))
#    print jarlist,dellist
#    return JsonResponse({'successlist' : jarlist, 'faillist' : dellist})
def backupfile(request):
    arg = request.POST.lists()[0][1]
    data = handledata(arg)
    successlist = data[0]
    faillist = data[1]
    rmap = data[2]
    for item in rmap:
        shutil.copytree(os.path.join(repo_path.get(item), 'lastest'), os.path.join(repo_path.get(item), time.strftime('%Y%m%d%H%M%S')))
    for item in successlist:
        temp = item.replace('-0.0.1-SNAPSHOT.jar', '').replace('.jar', '')
        shutil.copyfile(os.path.join('/fupload/lastest/', item), os.path.join(repo_path.get(repo_map.get(temp)), 'lastest/'+item))
    return JsonResponse({'successlist' : successlist, 'faillist' : faillist})

def updatefile(request):
    arg = request.POST.lists()[0][1]
    data = handledata(arg)
    successlist = data[0]
    faillist = data[1]
    rmap = data[2]
    data = execcommand(rmap)
    return JsonResponse({'successdata' : data, 'faillist' : faillist})

def repodir(request):
    repodir = []
    for item in repo_map:
        repodir.append({'label' : item, 'value': item})
    return JsonResponse({'repodir': repodir})

def prodir(request):
    projectdir = []
    dirname = repo_map.get(request.GET.get('dirname'))
    prodir = os.listdir(repo_path.get(dirname))
    print prodir
    prodir.remove('lastest')
    prodir.sort()
    for item in prodir:
        projectdir.append({'dir':item})
    return JsonResponse({'prodir' : projectdir, 'path': repo_path.get(dirname), 'project' : dirname})

def rollbackpath(request):
    sdir = request.POST.get('sdir')
    project = request.POST.get('project')
    rbpath = repo_path.get(project)
    shutil.move(os.path.join(rbpath, 'lastest'), os.path.join(rbpath, 'rollback'+sdir))
    shutil.copytree(os.path.join(rbpath, sdir), os.path.join(rbpath, 'lastest'))
    data = execcommand([project])
    return JsonResponse({'successdata' : data})

def deldir(request):
    deldir = request.POST.get('deldir')
    project = request.POST.get('project')
    rbpath = repo_path.get(project)
    os.system('rm -rf %s' % os.path.join(rbpath, deldir))
    return HttpResponse('true')

def prohosts(request):
    hosts = []
    project = request.GET.get('project')
    print project
    rmap = repo_map.get(project)
    print rmap
    hmap = host_map.get(rmap)
    for host in hmap:
        hosts.append({'host':host})
    return JsonResponse({'hosts' : hosts})

def cmdrun(request):
    tgt = request.POST.get('tgt')
    project = request.POST.get('project')
    spro = short_name.get(project)
    cmd = request.POST.get('cmd')
    data = execcmdrun(tgt, spro, cmd)
    return HttpResponse(data)
