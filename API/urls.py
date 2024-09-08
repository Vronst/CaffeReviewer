from django.urls import path
from . import views


urlpatterns = [
    path('cities/<str:city>/cafes/<str:cafe_name>/ratings', views.getRating, name='cafe-ratings'),
    path('cities/<str:city>/cafes/', views.getOrCreateCafes, name='city-cafes'),
    path('cities/<str:city>/cafes/<str:cafe_name>/', views.modifyCafe, name='modify-cafe'),
]