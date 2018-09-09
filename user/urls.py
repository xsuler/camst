from django.urls import path
from user import views


urlpatterns = [
    path('', views.login, name='login'),
    path('login', views.login, name = 'login'),
    path('regist', views.regist, name = 'regist'),
    path('index', views.index, name = 'index'),
    path('changepwd', views.changepwd, name = 'changepwd'),
]