from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Register your models here.
admin.site.register(MineUser, UserAdmin)
admin.site.register(Cafe)
admin.site.register(Category)
admin.site.register(Rating)
admin.site.register(Comments)
admin.site.register(City)
