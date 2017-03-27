import datetime
import socket
import struct

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from .models import User, LoginUser

def index(request):
    try:
        action = request.POST['action']
    except KeyError:
        # direct visit
        nid = search_login_user(request.META['REMOTE_ADDR'])
        if nid:
            return render(request, 'login/log_in_succeed.html', {'nid':nid})
        else:
            return render(request, 'login/log_in_site.html')
    else:
        # undirect visit
        if (action=='login'):
            nid_post, passwd_post = request.POST['nid'], request.POST['passwd']
    
            # clear the obsolete login information
            for loginuser in LoginUser.objects.all():
                if loginuser.time<timezone.now()-datetime.timedelta(days=1):
                    loginuser.delete()
                
            try:
                user = LoginUser.objects.get(nid=nid_post)
            except LoginUser.DoesNotExist:
                host = "1::1"
                port = 9734
                with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
                    s.connect((host, port))
                    login_request = nid_post.encode("utf-8")
                    if not (len(login_request)==10):
                        return render(request, 'login/log_in_site.html', {'error_message': "Wrong NID or PASSWORD."})
                    login_request += b'\0'+passwd_post.encode("utf-8")
                    if (len(login_request)>=32):
                        return render(request, 'login/log_in_site.html', {'error_message': "Wrong NID or PASSWORD."})
                    while (len(login_request)<32):
                        login_request += b'\0'
                    #login_request += socket.inet_pton(socket.AF_INET6, request.META["REMOTE_ADDR"])
                    login_request += socket.inet_pton(socket.AF_INET6, "1::2")
                    s.send(login_request)
                    data = s.recv(1024)
                    succeed = struct.unpack("<L", data[:4])[0]
                    nid = data[4:15].decode('utf-8')
                    lip = socket.inet_ntop(socket.AF_INET6, data[16:])
                    print(succeed, nid, lip)
                    
                if not (succeed):
                    return render(request, 'login/log_in_site.html', {'error_message': "Wrong NID or PASSWORD.",})
                else:
                    loginuser = LoginUser(nid=nid_post, lip=lip, time=timezone.now())
                    loginuser.save()
                    return render(request, 'login/log_in_succeed.html', {'nid':nid_post})
            else:
                return render(request, 'login/log_in_site.html', {'error_message': "This NID has already log in.",})
        else:
            ip = request.META['REMOTE_ADDR']
            for loginuser in LoginUser.objects.all():
                if (loginuser.lip==ip):
                    loginuser.delete()
                    return render(request, 'login/log_in_site.html')


def search_login_user(ip):
    for loginuser in LoginUser.objects.all():
        if (loginuser.lip==ip):
            return loginuser.nid
    return None
