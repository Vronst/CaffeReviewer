from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from CaffeRatings.models import Cafe, Rating
from .serializers import RatingSerializer


@api_view(['GET'])
def getRating(request, cafe_name):
    # cafe = Cafe.objects.get(name=cafe_name)
    cafe = get_object_or_404(Cafe, name=cafe_name)
    ratings = Rating.objects.filter(cafe=cafe)
    serializer = RatingSerializer(ratings, many=True)
    return Response(serializer.data)


'''
from django.http import JsonResponse
from CaffeRatings.models import Cafe, Rating

def get_rating(request, cafe_name):
    try:
        cafe = Cafe.objects.get(name=cafe_name)
        ratings = Rating.objects.filter(cafe=cafe)
        ratings_data = list(ratings.values())  # Convert QuerySet to a list of dictionaries
        return JsonResponse(ratings_data, safe=False)
    except Cafe.DoesNotExist:
        return JsonResponse({'error': 'Cafe not found'}, status=404)
'''