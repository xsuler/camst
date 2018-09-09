#coding=utf-8
from django.shortcuts import render, render_to_response, redirect, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from user.models import User
import markdown

#表单
class UserForm(forms.Form): 
    username = forms.CharField(label='用户名',max_length=100)
    password = forms.CharField(label='密码',widget=forms.PasswordInput())


#注册
def regist(req):
    if req.method == 'POST':
        username = req.POST.get("user", None)
        password = req.POST.get("pwd", None)
        #获取的表单数据与数据库进行比较
        user = User.objects.filter(username__exact = username)
        if user:
            #用户已经存在
            error_msg = "用户已经存在"
            return render(req, 'regist.html', {"error_msg": error_msg})
        else:
            #添加到数据库
            User.objects.create(username= username,password=password)
            error_msg = "注册成功"
            return render(req, 'regist.html', {"error_msg": error_msg})
    return render(req, 'regist.html')

#登录
def login(req):
    #清理cookie里保存username
    HttpResponse().delete_cookie('username')

    error_msg = ""
    if req.method == 'POST':
        username = req.POST.get("user", None)
        password = req.POST.get("pwd", None)
        #获取的表单数据与数据库进行比较
        user = User.objects.filter(username__exact = username)
        if user:
            if user.first().password == password:
                #比较成功，跳转index
                return render(req, 'index.html')
            else:
                #比较失败，还在login
                error_msg = "密码错误"
                return render(req, 'login.html', {"error_msg": error_msg})
        else:
            #比较失败，还在login
            error_msg = "用户名不存在"
            return render(req, 'login.html', {"error_msg": error_msg})
    return render(req, 'login.html')

#修改密码
def changepwd(req):
    error_msg = ""
    if req.method == 'POST':
        username = req.POST.get("user", None)
        password = req.POST.get("pwd", None)
        newpwd = req.POST.get("newpwd", None)
        #获取的表单数据与数据库进行比较
        user = User.objects.filter(username__exact = username)
        if user:
            if user.first().password == password:
                if len(newpwd) != 0:
                    user.first().delete()
                    User.objects.create(username= username,password=newpwd)
                    #比较成功，跳转index
                    error_msg = "修改密码成功"
                    response = render(req, 'changepwd.html', {"error_msg": error_msg})
                    return response
                else:
                    #比较失败，还在changepwd
                    error_msg = "请输入新密码"
                    return render(req, 'changepwd.html', {"error_msg": error_msg})
            else:
                #比较失败，还在changepwd
                error_msg = "原密码错误"
                return render(req, 'changepwd.html', {"error_msg": error_msg})
        else:
            #比较失败，还在changepwd
            error_msg = "用户名不存在"
            return render(req, 'changepwd.html', {"error_msg": error_msg})
    return render(req, 'changepwd.html')

#登陆成功
@login_required(login_url='/user/login')
def index(req):
    username = req.COOKIES.get('username','')
    return render(req, 'index.html' ,{'username':username})