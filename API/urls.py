from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from . import views


# TODO: Simplify urls to collection/item/collection at best if possible
urlpatterns = [
    path('cities/<str:city>/cafes/<str:cafe_name>/ratings', views.getRating, name='cafe-ratings'),
    path('cities/<str:city>/cafes/', views.getOrCreateCafes, name='city-cafes'),
    path('cities/<str:city>/cafes/<str:cafe_name>/', views.modifyCafe, name='modify-cafe'),
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]