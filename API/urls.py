from django.urls import path
from . import views


urlpatterns = [
    path('cafe/<cafe_name>', views.getRating, name='reviews'),
    path('city/<city>', views.getCafes, name='cafes')
]