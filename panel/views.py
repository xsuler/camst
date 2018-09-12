from django.shortcuts import render, redirect
from .models import User
from campip.models import Alarm
from .forms import LoginForm
import hashlib

# delete alarm
# time-order
# add user
# change pwd
# config alarm
# other detection
# mp4

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


def panel(request):
    is_auth = False
    form = LoginForm()
    alarms = []
    if 'is_auth' in request.session:
        is_auth = request.session['is_auth']
    if is_auth:
        alarms = Alarm.objects.order_by('time')

    context = {'is_auth': is_auth, 'alarms': alarms, 'form': form}
    return render(request, 'panel/panel.html', context)
