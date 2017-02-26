import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from .models import User, LoginUser

def index(request):
    return render(request, 'login/log_in_site.html')

def submit(request):
    try:
        nid_post, passwd_post = request.POST['nid'], request.POST['passwd']
    except KeyError:
        return render(request, 'login/log_in_site.html', {'error_message':"Wrong NID or PASSWORD.",})
    for loginuser in LoginUser.objects.all():
        if loginuser.time<timezone.now()-datetime.timedelta(days=1):
            loginuser.delete()
    try:
        user = LoginUser.objects.get(nid=nid_post)
    except LoginUser.DoesNotExist:
        return render(request, 'login/log_in_site.html', {'error_message': "This NID has already log in.",})
    try:
        user = User.objects.get(nid=nid_post, passwd=passwd_post)
    except User.DoesNotExist:
        return render(request, 'login/log_in_site.html', {'error_message': "Wrong NID or PASSWORD.",})
    else:
        loginuser = LoginUser(nid=nid_post, time=timezone.now())
        loginuser.save()
        return render(request, 'login/log_int_succeed.html')
