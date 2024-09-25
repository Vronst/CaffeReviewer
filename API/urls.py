from django.urls import path
from django.views.decorators.cache import cache_page
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from . import views


urlpatterns = [
    path('v1/cities/<str:city>/cafes/<str:cafe_name>/ratings', cache_page(60 * 15)(views.getRating), name='cafe-ratings'), # cached
    path('v1/cities/<str:city>/cafes/', views.getOrCreateCafes, name='city-cafes'),
    path('v1/cities/<str:city>/cafes/<str:cafe_name>/', views.modifyCafe, name='modify-cafe'),
    path('v1/cities/', views.getCities, name='cities'),
    path('v1/token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]