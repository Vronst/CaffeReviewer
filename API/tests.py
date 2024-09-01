from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from CaffeRatings.models import Cafe, Rating, MineUser, Category, City
from API.serializers import RatingSerializer

class GetRatingAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.city = City.objects.create(name="Test City")
        self.cafe = Cafe.objects.create(name="Test Cafe", location="123 Test St", city=self.city)
        self.user = MineUser.objects.create_user(username='testuser', password='testpassword')
        self.category = Category.objects.create(name="Service")
        self.rating = Rating.objects.create(cafe=self.cafe, author=self.user, category=self.category, rating=5, icon='star')
        
        self.valid_cafe_name = self.cafe.name
        self.invalid_cafe_name = "Nonexistent Cafe"

    def test_get_rating_valid_cafe(self):
        # Test case where cafe exists
        url = reverse('reviews', args=[self.valid_cafe_name])
        response = self.client.get(url)
        
        ratings = Rating.objects.filter(cafe=self.cafe)
        serializer = RatingSerializer(ratings, many=True, context={'request': response.wsgi_request}) # FIXME        
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_rating_invalid_cafe(self):
        # Test case where cafe does not exist
        url = reverse('reviews', args=[self.invalid_cafe_name])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'No Cafe matches the given query.')

