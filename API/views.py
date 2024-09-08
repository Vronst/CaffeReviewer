from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from CaffeRatings.models import Cafe, Rating, City
from .serializers import RatingSerializer, CafeSerializer, CafeDetailSerializer
from django.db.models import Avg, IntegerField
from django.db.models.functions import Cast
from django.core.exceptions import ObjectDoesNotExist
# TODO: Some authorization so not everyone can 
# create db entries with api


@api_view(['GET'])
def getRating(request, city, cafe_name):
    validation = get_object_or_404(City, name=city)
   
    cafe = get_object_or_404(Cafe, name=cafe_name, city=validation)
    ratings = Rating.objects.filter(cafe=cafe)
    serializer = RatingSerializer(ratings, many=True)

    return Response({'ratings': serializer.data})


@api_view(['GET', 'POST'])
def getOrCreateCafes(request, city):
    if request.method == 'GET':
        # annotating average_rating requires us to change its serializer
        # by adding SerializerMethodField
        cafes = Cafe.objects.filter(city__name=city).annotate(average_rating=Cast(Avg('rating__rating'), IntegerField()))
        serializer = CafeSerializer(cafes, many=True)

        if not cafes.exists():
            raise Http404('No cafes found')
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
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['PUT', 'PATCH'])
# def updateCafe(request, city, cafe_name):
#     validate_city = get_object_or_404(City, name=city)
#     cafe = get_object_or_404(Cafe, name=cafe_name, city=validate_city)
    
#     if request.data.get('city', None):
#         try:
#             retrived_city = City.objects.get(name=city)
#         except ObjectDoesNotExist:
#             retrived_city = City.objects.create(name=city)
#         request['city'] = retrived_city.id

#     if request.method == 'PUT':
#         serializer = CafeDetailSerializer(data=request.data)
#     elif request.method == 'PATCH':
#         serializer = CafeDetailSerializer(data=request.data, partial=True)
    
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     else:
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['DELETE', 'PUT', 'PATCH'])
def modifyCafe(request, city, cafe_name):
    validate_city = get_object_or_404(City, name=city)
    cafe = get_object_or_404(Cafe, name=cafe_name, city=validate_city)

    if request.method == 'DELETE':
        cafe.delete()

        return Response({'message': 'Cafe deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

    if request.data.get('city', None):
        try:
            retrived_city = City.objects.get(name=city)
        except ObjectDoesNotExist:
            retrived_city = City.objects.create(name=city)
        request.data['city'] = retrived_city.id

    if request.method == 'PUT':
        serializer = CafeDetailSerializer(cafe, data=request.data)
    elif request.method == 'PATCH':
        serializer = CafeDetailSerializer(cafe, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    