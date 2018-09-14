from django.urls import path
from . import views

urlpatterns = [
    path('', views.cam, name='cam'),
    path('refresh/', views.refresh, name='refresh')
]
