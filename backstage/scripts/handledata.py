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

def handledata(data):
    successlist = data
    rmap = []
    dellist = []
    for item in data:
        temp = item.replace('-0.0.1-SNAPSHOT.jar', '').replace('.jar', '')
        if repo_map.get(temp):
            rmap.append(repo_map.get(temp))
        else:
            dellist.append(item)
            success.remove(item)
    rmap = list(set(rmap))
    return (successlist, dellist, rmap)
