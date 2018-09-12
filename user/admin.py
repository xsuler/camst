from django.contrib import admin

# Register your models here.
from .models import User, superUser

admin.site.register(User)
admin.site.register(superUser)