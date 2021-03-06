from django.shortcuts import render, redirect, HttpResponse
from django.http import HttpResponseForbidden
from .models import User
from campip.models import Alarm, Region, Cam
import campip.views
from .forms import LoginForm, RegisterForm, ChangePswForm, RegionForm, CamForm
import hashlib


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username=form.cleaned_data['username'])
            if user is not None:
                if user.password == hashlib.sha224(
                        form.cleaned_data['password'].encode()).hexdigest():
                    request.session['is_auth'] = True
                    request.session['level'] = user.level
                    request.session['username'] = user.username
                    user.state = 1
                    user.save()
    if request.method == 'GET':
        request.session['is_auth'] = False
        user = User.objects.get(username=request.session['username'])
        user.state = 0
        user.save()
    return redirect('/panel/')


def getsession(request, key, default):
    res = default
    if key in request.session:
        res = request.session[key]
    return res


def getalarm(request):
    is_auth = getsession(request, 'is_auth', False)
    alarms = []
    usernm = getsession(request, 'username', 'stranger')
    if is_auth:
        alarms = Alarm.objects.order_by('-time')
        context = {'is_auth': is_auth, 'alarms': alarms, 'username': usernm}
        return render(request, 'panel/alarm.html', context)
    return HttpResponseForbidden()


def useropt(request, opt):
    is_auth = getsession(request, 'is_auth', False)
    if not is_auth:
        return HttpResponseForbidden()
    if opt == 0:
        if request.method == 'POST':
            form = ChangePswForm(request.POST)
            if form.is_valid():
                if 'username' in request.session:
                    user = User.objects.get(
                        username=request.session['username'])
                    if user.password == hashlib.sha224(
                            form.cleaned_data['oldpassword'].
                            encode()).hexdigest():
                        user.password = hashlib.sha224(
                            form.cleaned_data['newpassword'].
                            encode()).hexdigest()
                        user.state = 0
                        request.session['is_auth'] = False
                        user.save()
                        return redirect('/panel/')
    if opt == 1:
        if request.method == 'POST':
            form = RegisterForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                password2 = form.cleaned_data['password2']
                if User.objects.filter(username=username).count()==0:
                    if password == password2:
                        user = User(
                            username=username,
                            password=hashlib.sha224(
                                password.encode()).hexdigest())
                        user.save()
                return redirect('/panel/userpage')
    return HttpResponseForbidden()


def cameraopt(request, opt):
    is_auth = getsession(request, 'is_auth', False)
    if not is_auth:
        return HttpResponseForbidden()
    if opt == 0:
        if request.method == 'POST':
            form = CamForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['name']
                addr = form.cleaned_data['addr']
                cam = Cam(addr=addr, name=name)
                cam.save()
                return redirect('/panel/camera')
    return HttpResponseForbidden()


def configopt(request, opt):
    is_auth = getsession(request, 'is_auth', False)
    if not is_auth:
        return HttpResponseForbidden()
    if opt == 0:
        if request.method == 'POST':
            form = RegionForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['name']
                cover = form.cleaned_data['cover']
                delay = form.cleaned_data['delay']
                x = form.cleaned_data['x']
                y = form.cleaned_data['y']
                w = form.cleaned_data['w']
                h = form.cleaned_data['h']
                region = Region(
                    name=name, cover=cover, delay=delay, x=x, y=y, w=w, h=h)
                region.save()
                return redirect('/panel/config')
    return HttpResponseForbidden()


def camera(request):
    is_auth = getsession(request, 'is_auth', False)
    form_cam = CamForm()
    cams = Cam.objects.all()
    usernm = getsession(request, 'username', 'stranger')
    if is_auth:
        context = {
            'is_auth': is_auth,
            'form_cam': form_cam,
            'cams': cams,
            'username': usernm,
            'host_live': 'http://' + request.META['HTTP_HOST'] + '/live'
        }
        return render(request, 'panel/camera.html', context)
    return HttpResponseForbidden()


def config(request):
    is_auth = getsession(request, 'is_auth', False)
    form_cfg = RegionForm()
    regions = Region.objects.all()
    usernm = getsession(request, 'username', 'stranger')
    if is_auth:
        context = {
            'is_auth': is_auth,
            'form_cfg': form_cfg,
            'regions': regions,
            'username': usernm
        }
        return render(request, 'panel/config.html', context)
    return HttpResponseForbidden()


def userpage(request):
    is_auth = getsession(request, 'is_auth', False)
    is_god = getsession(request, 'level', 0) == 0
    form_pwd = ChangePswForm()
    form_reg = RegisterForm()
    userlist = []
    usernm = getsession(request, 'username', 'stranger')
    if is_god:
        userlist = User.objects.filter(level=1)
    if is_auth:
        context = {
            'is_auth': is_auth,
            'is_god': is_god,
            'form_pwd': form_pwd,
            'form_reg': form_reg,
            'userlist': userlist,
            'username': usernm
        }
        return render(request, 'panel/manage.html', context)
    return HttpResponseForbidden()


def panel(request):
    is_auth = getsession(request, 'is_auth', False)
    usernm = getsession(request, 'username', 'stranger')
    form = LoginForm()
    alarms = []
    context = {
        'is_auth': is_auth,
        'alarms': alarms,
        'form': form,
        'username': usernm,
        'host_live': 'http://' + request.META['HTTP_HOST'] + '/live'
    }
    return render(request, 'panel/panel.html', context)


def choosecam(request, pk):
    is_auth = getsession(request, 'is_auth', False)
    if not is_auth:
        return HttpResponseForbidden()
    campip.views.camaddr = Cam.objects.get(pk=pk).addr
    return HttpResponse('ok')


def delregion(request, pk):
    is_auth = getsession(request, 'is_auth', False)
    if not is_auth:
        return HttpResponseForbidden()
    Region.objects.get(pk=pk).delete()
    return HttpResponse('ok')


def deluser(request, pk):
    is_auth = getsession(request, 'is_auth', False)
    is_god = getsession(request, 'level', 0) == 0
    if not is_auth or not is_god:
        return HttpResponseForbidden()
    User.objects.get(pk=pk).delete()
    return HttpResponse('ok')


def delalarm(request, pk):
    is_auth = getsession(request, 'is_auth', False)
    if is_auth:
        Alarm.objects.get(pk=pk).delete()
        return HttpResponse('ok')
    return HttpResponseForbidden()
