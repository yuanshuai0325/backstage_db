import os
import time
import shutil

def backupjar(jarlist):
    map = []
    dellist = []
    repo_map = {
        'as-gateway-web': 'asgw',
        'as-interface-monitor':'asmsrv',
        'as-service-monitor':'asmsrv',
        'as-service-push':'asmsrv',
        'rc-service-code':'code',
        'rc-service-share':'code',
        'bbs':'gw',
        'rc-gateway-web':'gw',
        'rc-service-common':'msrv',
        'rc-service-file':'msrv',
        'rc-service-monitor':'msrv',
        'rc-service-msg':'msrv',
        'rc-service-solr':'msrv',
        'rc-service-user':'msrv',
        'rc-service-ofs':'tmsrv',
        'rc-service-itm':'tmsrv'
    }
    repo_path = {
        'asgw': '/repo/tongren/asgw',
        'asmsrv': '/repo/tongren/asmsrv',
        'code': '/repo/tongren/code',
        'gw': '/repo/tongren/gw',
        'msrv': '/repo/tongren/msrv',
        'tmsrv': '/repo/tongren/tmsrv',
    }
    for item in jarlist:
        temp = item.replace('-0.0.1-SNAPSHOT.jar', '').replace('.jar', '')
        if repo_map.get(temp):
            map.append(repo_map.get(temp))
        else:
            dellist.append(item)
            jarlist.remove(item)
    map = set(map)
    for item in map:
        shutil.copytree(os.path.join(repo_path.get(item), 'lastest'), os.path.join(repo_path.get(item), time.strftime('%Y%m%d%H%M%S')))
    for item in jarlist:
        temp = item.replace('-0.0.1-SNAPSHOT.jar', '').replace('.jar', '')
        shutil.copyfile(os.path.join('/fupload/lastest/', item), os.path.join(repo_path.get(repo_map.get(temp)), 'lastest/'+item))



testlist=["as-gateway-web-0.0.1-SNAPSHOT.jar","rc-service-code-0.0.1-SNAPSHOT.jar","bbs.jar", "xx.txt"]



backupjar(testlist)
