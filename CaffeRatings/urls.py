from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("<str:city>", views.city_load, name="city"),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('register/', views.register, name='registration')
]