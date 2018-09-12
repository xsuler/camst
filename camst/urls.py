from django.urls import path,include

urlpatterns = [
    path('live', include('campip.urls')),
    path('panel/', include('panel.urls')),
]
