from django.urls import path
from . import views


urlpatterns = [
    path('<cafe_name>', views.getRating, name='reviews')
]