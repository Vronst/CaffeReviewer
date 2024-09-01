from django.urls import path
# from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("<str:city>", views.city_load, name="city"),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.register, name='registration'),
    path('account/', views.account_settings, name='account_settings'),
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('logout/', views.custom_logout, name='logout')
]