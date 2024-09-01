from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from CaffeRatings.models import Cafe, Rating, MineUser, Category, City
from API.serializers import RatingSerializer, CafeSerializer
from django.db.models import Avg, IntegerField
from django.db.models.functions import Cast

class GetRatingAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.city = City.objects.create(name="Test City")
        self.cafe = Cafe.objects.create(name="Test Cafe", location="123 Test St", city=self.city)
        self.user = MineUser.objects.create_user(username='testuser', password='testpassword')
        self.category = Category.objects.create(name="Service")
        self.rating = Rating.objects.create(cafe=self.cafe, author=self.user, category=self.category, rating=5, icon='star')
        
        self.valid_cafe_name = self.cafe.name
        self.invalid_cafe_name = "NonExistent Cafe"
        
        self.invalidCity = 'NoneExistentCity'
        self.validCity = self.city.name

    def test_get_rating_valid_cafe(self):
        # Test case where cafe exists
        url = reverse('reviews', args=[self.valid_cafe_name])
        response = self.client.get(url)
        
        ratings = Rating.objects.filter(cafe=self.cafe)
        serializer = RatingSerializer(ratings, many=True)      
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_rating_invalid_cafe(self):
        # Test case where cafe does not exist
        url = reverse('reviews', args=[self.invalid_cafe_name])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'No Cafe matches the given query.')

    def test_get_all_existing_cafes_in_city(self):
        url = reverse('cafes', args=[self.validCity])
        response = self.client.get(url)

        cafes = Cafe.objects.filter(city__name=self.validCity).annotate(average_rating=Cast(Avg('rating__rating'), IntegerField()))
        serializer = CafeSerializer(cafes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_all_existing_cafes_in_city(self):
        url = reverse('cafes', args=[self.invalidCity])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "No cafes found")
