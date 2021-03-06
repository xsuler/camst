from django.urls import path

from . import views

urlpatterns = [
    path('', views.panel, name='panel'),
    path('login/', views.login, name='login'),
    path('delalarm/<int:pk>', views.delalarm, name='delalarm'),
    path('getalarm/', views.getalarm, name='getalarm'),
    path('userpage/', views.userpage, name='userpage'),
    path('config/', views.config, name='config'),
    path('camera/', views.camera, name='camera'),
    path('userpage/opt/<int:opt>', views.useropt, name='useropt'),
    path('config/opt/<int:opt>', views.configopt, name='connfigopt'),
    path('camera/opt/<int:opt>', views.cameraopt, name='cameraopt'),
    path('userpage/deluser/<int:pk>', views.deluser, name='deluser'),
    path('config/delregion/<int:pk>', views.delregion, name='delregion'),
    path('camera/choosecam/<int:pk>', views.choosecam, name='choosecam'),
]
