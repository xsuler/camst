from django.urls import path

from . import views

urlpatterns = [
    path('', views.panel, name='panel'),
    path('login/', views.login, name='login'),
    path('delalarm/<int:pk>', views.delalarm, name='delalarm'),
    path('getalarm/', views.getalarm, name='getalarm'),
    path('userpage/', views.userpage, name='userpage'),
    path('userpage/opt/<int:opt>', views.useropt, name='useropt'),
    path('userpage/deluser/<int:pk>', views.deluser, name='deluser')
]
