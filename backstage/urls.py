from django.conf.urls import url
from backstage.views import adduser, deluser, veruser, userinfo, getalluser, chname, chpasswd, admincpw, chstatus, chrole, queryuser, postfile, delfile, listfile, backupfile, updatefile, repodir, prodir, rollbackpath, deldir, prohosts, cmdrun

urlpatterns = [
    url(r'adduser', adduser),
    url(r'deluser', deluser),
    url(r'veruser', veruser),
    url(r'userinfo', userinfo),
    url(r'getalluser', getalluser),
    url(r'chname', chname),
    url(r'chpasswd', chpasswd),
    url(r'admincpw', admincpw),
    url(r'chstatus', chstatus),
    url(r'chrole', chrole),
    url(r'queryuser', queryuser),
    url(r'postfile', postfile),
    url(r'delfile', delfile),
    url(r'listfile', listfile),
    url(r'backupfile', backupfile),
    url(r'updatefile', updatefile),
    url(r'repodir', repodir),
    url(r'prodir', prodir),
    url(r'rollbackpath', rollbackpath),
    url(r'deldir', deldir),
    url(r'prohosts', prohosts),
    url(r'cmdrun', cmdrun),
]
