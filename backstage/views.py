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
    name, password, status, role = request.POST.get('username'), generate_password_hash(str(request.POST.get('password'))), request.POST.get('status'), request.POST.get('role')
    if status:
        status = "1"
    else:
        status = "0"
    if UserInfo.objects.filter(name=name):
        reason = "用户 %s 已存在" % name
        return JsonResponse({'exec':'false', 'reason': reason})
    if not Status.objects.filter(id=status):
        reason = "用户状态不存在"
        return JsonResponse({'exec':'false', 'reason': reason})
    if not Role.objects.filter(id=role):
        reason = "用户角色不存在"
        return JsonResponse({'exec':'false', 'reason': reason})
    try:
        adddata = UserInfo(name=name, password=password, status_id=status, role_id=role)
        adddata.save()
        reason = "用户 %s 添加成功" % name
        return JsonResponse({'exec': 'true', 'reason': reason})
    except Exception as e:
        reason = "用户 %s 添加失败" % name
        return JsonResponse({'exec':'false', 'reason': reason})

def deluser(request):
    id = request.POST.get('userid')
    name = request.POST.get('username')
    try:
        data = UserInfo.objects.get(id=id)
    except Exception as e:
        return JsonResponse({'exec':'false', 'reason': '用户userid不存在'})
    if data.name != name:
        reason = "userid 对应用户名 %s 不存在" % name
        return JsonResponse({'exec':'false', 'reason': reason})
    try:
        UserInfo.objects.filter(id=id).delete()
        reason = "用户 %s 已删除" % name
        return JsonResponse({'exec':'true', 'reason': reason})
    except Exception as e:
        reason = "用户 %s 删除失败" % name
        return JsonResponse({'exec':'false', 'reason': reason})

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
    elif int(code) != data.status_id:
        return JsonResponse({'exec':'false', 'reason':'用户被禁用'}) 
    else:
        return JsonResponse({'exec':'true', 'username' : name, 'userid' : userid, 'status' : status, 'code' : code, 'role':[role]})

def getalluser(request):
    newdata = []
    try:
        data = UserInfo.objects.values('id', 'name','status','role__urole')
        for item in data:
            print item['status']
            #newdata.append({'userid':item['id'], 'username':item['name'], 'xcode':'x', 'role':item['role__urole']})
            newdata.append({'userid':item['id'], 'username':item['name'], 'xcode':('启用' if str(item['status']) == '1' else '禁用'), 'role':item['role__urole']})
    except Exception as e:
        return JsonResponse({'exec':'false', 'reason':'数据库获取失败'})
    return JsonResponse({'exec':'true', 'data':newdata})

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
    print '*'*10
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

def admincpw(request):
    print '-'*10
    id = str(request.POST.get('userid'))
    name = request.POST.get('username')
    password = generate_password_hash(str(request.POST.get('password')))
    try:
        data = UserInfo.objects.get(id=id)
    except Exception as e:
        reason = 'userid %s 不存在' % id
        return JsonResponse({'exec':'false', 'reason':reason})
    print '-'*10
    print data.name
    if name != data.name:
        reason = '用户 %s 与userid不符'
        return JsonResponse({'exec':'false', 'reason':reason})
    try:
        UserInfo.objects.filter(id=id).update(password=password)
    except Exception as e:
        return JsonResponse({'exec':'false', 'reason':'密码修改失败'})
    reason = '用户 %s 密码修改成功' % name
    return JsonResponse({'exec':'true', 'reason':reason})

def chstatus(request):
    id = request.POST.get('userid')
    name = request.POST.get('username')
    xcode = request.POST.get('xcode')
    print id, name, xcode
    code = 1 if xcode == "启用" else 2
    try:
        data = UserInfo.objects.get(id=id)
    except Exception as e:
        reason = 'userid %s 不存在' % id
        return JsonResponse({'exec':'false', 'reason':reason})
    if name != data.name:
        reason = '用户 %s 与userid不符'
        return JsonResponse({'exec':'false', 'reason':reason})
    try:
        UserInfo.objects.filter(id=id).update(status=code)
        reason = '用户 %s 已 %s' % (name, xcode)
        return JsonResponse({'exec':'true', 'reason':reason})
    except Exception as e:
        reason = '用户 %s %s 失败' % (name, xcode)
        return JsonResponse({'exec':'false', 'reason':reason})

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
    try:
        for item in repo_map:
            repodir.append({'label' : item, 'value': item})
        return JsonResponse({'exec':'true','repodir': repodir})
    except Exception as e:
        reason = "repo_map列表获取失败"
        return JsonResponse({'exec':'false', 'reason':reason})

def prodir(request):
    projectdir = []
    try:
        dirname = repo_map.get(request.GET.get('dirname'))
        prodir = os.listdir(repo_path.get(dirname))
        print prodir
        prodir.remove('lastest')
        prodir.sort()
        for item in prodir:
            projectdir.append({'dir':item})
        return JsonResponse({'exec' : 'true', 'prodir' : projectdir, 'path': repo_path.get(dirname), 'project' : dirname})
    except Exception as e:
        reason = "项目信息获取失败"
        return JsonResponse({'exec':'false', 'reason':reason})

def rollbackpath(request):
    try:
        sdir = request.POST.get('sdir')
        project = request.POST.get('project')
        rbpath = repo_path.get(project)
        shutil.move(os.path.join(rbpath, 'lastest'), os.path.join(rbpath, 'rollback'+sdir))
        shutil.copytree(os.path.join(rbpath, sdir), os.path.join(rbpath, 'lastest'))
        data = execcommand([project])
        return JsonResponse({'exec' : 'true', 'successdata' : data})
    except Exception as e:
        print e
        reason = "%s %s 回退失败" % (project, sdir)
        return JsonResponse({'exec' : 'false', 'reason' : reason})

def deldir(request):
    try:
        deldir = request.POST.get('deldir')
        project = request.POST.get('project')
        rbpath = repo_path.get(project)
        os.system('rm -rf %s' % os.path.join(rbpath, deldir))
        reason = "%s %s 已删除" % (project, deldir)
        return JsonResponse({'exec' : 'true', 'reason':reason})
    except Exception as e:
        reason = "%s %s 删除失败" % (project, deldir)
        return JsonResponse({'exec' : 'false', 'reason':reason})

def prohosts(request):
    hosts = []
    project = request.GET.get('project')
    print project
    try:
        rmap = repo_map.get(project)
        print rmap
        hmap = host_map.get(rmap)
        for host in hmap:
            hosts.append({'host':host})
        return JsonResponse({'exec':'true', 'hosts' : hosts})
    except Exception as e:
        reason = "未获取到 %s" % project 
        return JsonResponse({'exec':'false', 'reason':reason})

def cmdrun(request):
    try:
        tgt = request.POST.get('tgt')
        project = request.POST.get('project')
        spro = short_name.get(project)
        cmd = request.POST.get('cmd')
        data = execcmdrun(tgt, spro, cmd)
        return JsonResponse({'exec':'true', 'cmdreturn':data})
    except Exception as e:
        reason  = "%s %s %s 执行失败" % (tgt, project, cmd)
        return JsonResponse({'exec':'false', 'reason':reason})
