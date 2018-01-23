#!/usr/bin/env python
#-*- coding=utf8 -*-
import os
import sys
import json
import subprocess
from salt.utils import get_colors
from salt.output.nested import NestDisplay

curentdir = os.path.dirname(os.path.realpath(__file__)).split('/')
curentdir.pop()
curentdir.pop()
fatherdir = '/'.join(curentdir)

sys.path.append(fatherdir)

os.environ['DJANGO_SETTINGS_MODULE'] = 'backstage_db.settings'
import django
django.setup()
from backstage.models import Repo, Project, Hosts, Server

# call salt output class
class NestPut(NestDisplay):
    def __init__(self):
        self.colors = get_colors(True)
        self.__dict__.update(get_colors(True))
        self.strip_colors = True

def Prest(data):
    '''
    Display ret data
    '''
    nest = NestPut()
    return '\n'.join(nest.display(data, 0, '', []))

#repo_map = { 
#    'rc-gateway-web':'gw',
#    'bbs':'gw',
#    'rc-service-common':'msrv',
#    'rc-service-file':'msrv',
#    'rc-service-monitor':'msrv',
#    'rc-service-msg':'msrv',
#    'rc-service-solr':'msrv',
#    'rc-service-user':'msrv',
#    'rc-service-ofs':'tmsrv',
#    'rc-service-itm':'tmsrv',
#    'rc-service-code':'code',
#    'rc-service-share':'code',
#    'as-gateway-web': 'asgw',
#    'as-interface-monitor':'asmsrv',
#    'as-service-monitor':'asmsrv',
#    'as-service-push':'asmsrv',
#}
#short_name = {
#    'rc-gateway-web':'gateway',
#    'bbs':'bbs',
#    'rc-service-common':'common',
#    'rc-service-file':'file',
#    'rc-service-monitor':'monitor',
#    'rc-service-msg':'msg',
#    'rc-service-solr':'solr',
#    'rc-service-user':'user',
#    'rc-service-ofs':'ofs',
#    'rc-service-itm':'itm',
#    'rc-service-code':'code',
#    'rc-service-share':'share',
#    'as-gateway-web': 'as-gateway',
#    'as-interface-monitor':'as-interface-monitor',
#    'as-service-monitor':'as-monitor',
#    'as-service-push':'as-push',
#}
#repo_path = { 
#    'gw': '/repo/tongren/gw',
#    'msrv': '/repo/tongren/msrv',
#    'tmsrv': '/repo/tongren/tmsrv',
#    'code': '/repo/tongren/code',
#    'asgw': '/repo/tongren/asgw',
#    'asmsrv': '/repo/tongren/asmsrv',
#}
#host_map = {
#    'gw': ['154-100.test.com', 'client-102.test.com'],
#    'msrv': ['test-101.test.com', 'client-102.test.com'],
#    'tmsrv': ['154-100.test.com', 'client-102.test.com'],
#    'code': ['154-100.test.com', 'test-101.test.com'],
#    'asgw': ['client-102.test.com'],
#    'asmsrv': ['test-101.test.com'],
#}
#remote_dir = {
#    'gw': '/opt/rc/app/',
#    'msrv': '/opt/rc/app/',
#    'tmsrv': '/opt/rc/app/',
#    'code': '/opt/rc/app/',
#    'asgw': '/opt/as/app/',
#    'asmsrv': '/opt/as/app/',
#}
#rsync_server = '192.168.154.100'

def handledata(data):
    successlist = data[:]
    rmap = []
    dellist = []
    for item in data:
        print item
        temp = item.replace('-0.0.1-SNAPSHOT.jar', '').replace('.jar', '')
        #if repo_map.get(temp):
        #    rmap.append(repo_map.get(temp))
        try:
            data = Project.objects.get(name=temp)
            rmap.append(data.repo.name)
        except Exception as e:
            dellist.append(item)
            successlist.remove(item)
  #      if data.repo.repo:
  #          rmap.append(data.repo.repo)
  #      else:
  #          dellist.append(item)
  #          successlist.remove(item)
  #  rmap = list(set(rmap))
    return (successlist, dellist, rmap)

def handlesalt(result):
    data = json.loads(result).get("return")
    for index,item in enumerate(data):
        for itemin in item:
            if data[index][itemin] != False:
                data[index][itemin] =  data[index][itemin].replace('\n','')
    return data

def execcommand(data):
    commands = {}
    results = {}
    tmp = Server.objects.all()
    for server in tmp:
        rsync_server = server.name 
    #print rsync_server
    for item in data:
        hosts = []
        try:
            data = Repo.objects.get(name=item)
            repo_id = data.id
            path = data.rpath
     #       print repo_id,path
            data = Hosts.objects.filter(repo_id=repo_id)
            for tmp in data:
                hosts.append(tmp.host)
            #path = remote_dir.get(item)
            #hosts = host_map.get(item)
        except Exception as e:
            return '执行失败 %s' % e
        commands[item] = ("pepper -L '%s' cmd.run 'rsync -av --password-file=/etc/rsync.pass --delete --exclude logs root@%s::%s %s'" % (','.join(hosts), rsync_server, item, path))
    print commands
    for execitem in commands:
        result = subprocess.Popen(commands[execitem], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.read()
        #results[execitem] = Prest(json.loads(result).get("return"))
        execdata = handlesalt(result)
        results[execitem] = execdata
        print results
    return results

def execcmdrun(tgt, pro, cmd):
    command = "pepper '%s' cmd.run 'supervisorctl %s %s'" % (tgt, cmd, pro)
    result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.read()
    execdata = json.loads(result).get("return")
    for item in execdata[0]:
        host = item
        if execdata[0][host] != False:
            data = execdata[0][host].split('\n')
        else:
            data = ['执行结果为 %s' % execdata[0][host]]
    print data
    return {'host':host,'data':data}


#print handledata(['rc-service-monitor-0.0.1-SNAPSHOT.jar'])
#print execcommand(['msrv'])
