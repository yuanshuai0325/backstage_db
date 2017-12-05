from django.conf.urls import url
from backstage.views import adduser, deluser, veruser, chname, chpasswd, chstatus, chrole, queryuser, postfile, delfile, listfile

urlpatterns = [
    url(r'adduser', adduser),
    url(r'deluser', deluser),
    url(r'veruser', veruser),
    url(r'chname', chname),
    url(r'chpasswd', chpasswd),
    url(r'chstatus', chstatus),
    url(r'chrole', chrole),
    url(r'queryuser', queryuser),
    url(r'postfile', postfile),
    url(r'delfile', delfile),
    url(r'listfile', listfile),
]
