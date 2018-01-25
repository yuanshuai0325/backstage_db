insert into backstage_repo(name, lpath, rpath) values('gw', '/repo/tongren/gw', '/opt/rc/app/');
insert into backstage_repo(name, lpath, rpath) values('msrv', '/repo/tongren/msrv', '/opt/rc/app/');
insert into backstage_repo(name, lpath, rpath) values('tmsrv', '/repo/tongren/tmsrv', '/opt/rc/app/');
insert into backstage_repo(name, lpath, rpath) values('code', '/repo/tongren/code', '/opt/rc/app/');
insert into backstage_repo(name, lpath, rpath) values('asgw', '/repo/tongren/asgw', '/opt/as/app/');
insert into backstage_repo(name, lpath, rpath) values('asmsrv', '/repo/tongren/asmsrv', '/opt/as/app/');


insert into backstage_project(name, sname, repo_id) values('rc-gateway-web', 'gateway', 1);
insert into backstage_project(name, sname, repo_id) values('bbs', 'bbs', 1);
insert into backstage_project(name, sname, repo_id) values('rc-service-common', 'common', 2);
insert into backstage_project(name, sname, repo_id) values('rc-service-file', 'file', 2);
insert into backstage_project(name, sname, repo_id) values('rc-service-monitor', 'monitor', 2);
insert into backstage_project(name, sname, repo_id) values('rc-service-msg', 'msg', 2);
insert into backstage_project(name, sname, repo_id) values('rc-service-user', 'user', 2);
insert into backstage_project(name, sname, repo_id) values('rc-service-solr', 'solr', 2);
insert into backstage_project(name, sname, repo_id) values('rc-service-ofs', 'ofs', 3);
insert into backstage_project(name, sname, repo_id) values('rc-service-itm', 'itm', 3);
insert into backstage_project(name, sname, repo_id) values('rc-service-code', 'code', 4);
insert into backstage_project(name, sname, repo_id) values('rc-service-share', 'share', 4);
insert into backstage_project(name, sname, repo_id) values('as-gateway-web', 'as-gateway', 5);
insert into backstage_project(name, sname, repo_id) values('as-service-monitor', 'as-monitor', 6);
insert into backstage_project(name, sname, repo_id) values('as-service-push', 'as-push', 6);
insert into backstage_project(name, sname, repo_id) values('as-interface-monitor', 'as-interface-monitor', 6);


insert into backstage_hosts(host, repo_id) values('154-100.test.com', 1);
insert into backstage_hosts(host, repo_id) values('client-102.test.com', 1);
insert into backstage_hosts(host, repo_id) values('test-101.test.com', 2);
insert into backstage_hosts(host, repo_id) values('client-102.test.com', 2);
insert into backstage_hosts(host, repo_id) values('154-100.test.com', 3);
insert into backstage_hosts(host, repo_id) values('client-102.test.com', 3);
insert into backstage_hosts(host, repo_id) values('154-100.test.com', 4);
insert into backstage_hosts(host, repo_id) values('test-101.test.com', 4);
insert into backstage_hosts(host, repo_id) values('client-102.test.com', 5);
insert into backstage_hosts(host, repo_id) values('test-101.test.com', 6);


insert into backstage_server(name) values('154-100.test.com');
