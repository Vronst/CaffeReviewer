from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from django.db.models import Avg, IntegerField
from django.db.models.functions import Cast
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.utils.text import slugify # making keys safe for other caches
from CaffeRatings.models import Cafe, Rating, City
from .serializers import (
    RatingSerializer,
    CafeSerializer,
    CafeDetailSerializer,
    CitySerializer,
    GroupBasedTokenObtainPairSerializer,
)
from .permissions import CustomTokenPermission


# cached in urls.py
@api_view(['GET'])
@permission_classes([AllowAny])
def getRating(request: Request, city: str, cafe_name: str) -> Response:
    # validation = get_object_or_404(City, name=city)
   
    # cafe = get_object_or_404(Cafe, name=cafe_name, city=validation)    
    # ratings = Rating.objects.filter(cafe=cafe)
    ratings = Rating.objects.filter(cafe__name=cafe_name, cafe__city__name=city)
    if not ratings.exists():
        raise Http404('No match for provided details')

    serializer = RatingSerializer(ratings, many=True)

    return Response({'ratings': serializer.data})


@api_view(['GET', 'POST'])
@permission_classes([CustomTokenPermission])
def getOrCreateCafes(request:Request, city: str) -> Response:
    if request.method == 'GET':
        if cache.get(slugify(city)):
            return Response(cache.get(slugify(city)))
        
        # annotating average_rating requires us to change its serializer
        # by adding SerializerMethodField
        cafes = Cafe.objects.filter(city__name=city).annotate(average_rating=Cast(Avg('rating__rating'), IntegerField()))
        serializer = CafeSerializer(cafes, many=True)

        if not cafes.exists():
            raise Http404('No cafes found')
        
        cache.set(slugify(city), serializer.data, timeout=60*60)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        try:
            api_city = City.objects.get(name=city)
            # if cafe is first cafe in city
            # the city does not exists yet
            # so we need to create one
        except ObjectDoesNotExist:
            api_city = City.objects.create(name=city)
        request.data['city'] = api_city.id
            
        # try:
        #     request.data['approved']
        # except KeyError:
        #     request.data['approved'] = True

        request.data['approved'] = request.data.get('approved', True)
            
        serializer = CafeDetailSerializer(data=request.data)
        if serializer.is_valid():
            cache.delete(slugify(city)) # deleting invalid data
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated, CustomTokenPermission])
# @authentication_classes([])
def modifyCafe(request: Request, city: str, cafe_name: str) -> Response:
    cafe = Cafe.objects.select_related('city').filter(city__name=city, name=cafe_name).first()
    if request.method == 'DELETE':
        if not cafe:
            return Response({'message': 'Invalid Cafe'}, status=status.HTTP_400_BAD_REQUEST)
        cache.delete(slugify(city)) # deleting invalid data
        cafe.delete()

        return Response({'message': 'Cafe deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

    if request.data.get('city', None):
        try:
            # retrived_city = City.objects.get(name=city)
            retrived_city = cafe.city
        except ObjectDoesNotExist:
            retrived_city = City.objects.create(name=city)
        request.data['city'] = retrived_city.id

    if request.method == 'PUT':
        serializer = CafeDetailSerializer(cafe, data=request.data)
    elif request.method == 'PATCH':
        serializer = CafeDetailSerializer(cafe, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        cache.delete(slugify(city)) # deleting invalid data
        return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes([AllowAny])
def getCities(request:Request) -> Response:
    data = City.objects.all()
    serializer = CitySerializer(data, many=True)
    return Response({'Cities': serializer.data}, status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = GroupBasedTokenObtainPairSerializer
