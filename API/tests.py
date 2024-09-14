from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from CaffeRatings.models import Cafe, Rating, MineUser, Category, City
from API.serializers import RatingSerializer, CafeSerializer
from django.db.models import Avg, IntegerField
from django.db.models.functions import Cast

class GetRatingAPITest(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.city = City.objects.create(name="Test City")
        self.cafe = Cafe.objects.create(name="Test Cafe", location="123 Test St", city=self.city, image='image')

        self.user = MineUser.objects.create_user(username='testuser', password='testpassword')
        self.adminUser = MineUser.objects.create_user(username='adminUser', password='adminpassword')

        self.adminUser.groups.create(name='admin')
        
        self.category = Category.objects.create(name="Service")
        self.rating = Rating.objects.create(cafe=self.cafe, author=self.user, category=self.category, rating=5, icon='star')
        
        self.valid_cafe_name = self.cafe.name
        self.invalid_cafe_name = "NonExistent Cafe"
        
        self.invalidCity = 'NoneExistentCity'
        self.validCity = self.city.name

        self.token = self.get_user_token(self.adminUser)

    def get_user_token(self, user) -> str:
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_get_rating_valid_cafe(self) -> None:
        # Test case where cafe exists
        url = reverse('cafe-ratings', args=[self.validCity, self.valid_cafe_name])
        response = self.client.get(url)
        
        ratings = Rating.objects.filter(cafe=self.cafe)
        serializer = RatingSerializer(ratings, many=True)      
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'ratings': serializer.data})

    def test_get_rating_invalid_cafe(self) -> None:
        # Test case where cafe does not exist
        url = reverse('cafe-ratings', args=[self.validCity, self.invalid_cafe_name])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'No Cafe matches the given query.')

    def test_get_rating_invalid_city(self) -> None:
        # Test case where cafe does not exist
        url = reverse('cafe-ratings', args=[self.invalidCity, self.invalid_cafe_name])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'No City matches the given query.')


    def test_get_all_existing_cafes_in_city(self) -> None:
        url = reverse('city-cafes', args=[self.validCity])
        response = self.client.get(url)

        cafes = Cafe.objects.filter(city__name=self.validCity).annotate(average_rating=Cast(Avg('rating__rating'), IntegerField()))
        serializer = CafeSerializer(cafes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_all_nonexisting_cafes_in_city(self) -> None:
        url = reverse('city-cafes', args=[self.invalidCity])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "No cafes found")

    def test_valid_cafe_creation(self) -> None:
        url = reverse('city-cafes', args=[self.validCity])
        data = {
            'name': 'APICREATE',
            'location': 'API TEST',
        }
        # self.client.login(username='adminUser', password='adminpassword')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Cafe.objects.get(name='APICREATE', city=self.city).name,
            'APICREATE'
            )
    
    def test_valid_cafe_creation_with_city(self) -> None:
        city = 'NOcityHERE'
        url = reverse('city-cafes', args=[city])
        data = {
            'name': 'APICREATE1',
            'location': 'API TEST',
        }

        # self.client.login(username='adminUser', password='adminpassword')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.post(url, data, format='json')

        city_id = City.objects.get(name=city).id
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Cafe.objects.get(name='APICREATE1', city=city_id).name,
            'APICREATE1'
            )
        self.assertTrue(City.objects.filter(name=city).exists(), 'Failed creating city')
        self.assertEqual(City.objects.filter(name=city).count(), 1, 'No city in database after creation')

    
    def test_create_duplicate(self) -> None:
        url = reverse('city-cafes', args=[self.validCity])
        data = {
            'name': 'APICREATE3',
            'location': 'API TEST',
        }

        # self.client.login(username='adminUser', password='adminpassword')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        response1 = self.client.post(url, data, format='json')
        response2 = self.client.post(url, data, format='json')

        self.assertEqual(response1.status_code, status.HTTP_201_CREATED, 'Failed first creation request')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST, 'Failed second creation (duplication) request')

    def test_invalid_cafe_creation(self) -> None:
        url = reverse('city-cafes', args=[self.validCity])
        data = {
            'location': 'API TEST',
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_update_PUT_full(self) -> None:
        url = reverse('modify-cafe', args=[self.validCity, self.valid_cafe_name])
        name, location, image = 'UPDATEapi', 'UPDATElocation', 'UPDATEimage'
        data = {
            'name': name,
            'location': location,
            'city': self.city.id,
            'image': image
        }

        # self.client.login(username='adminUser', password='adminpassword')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, None) # probably pointless

        updated_cafe = Cafe.objects.get(name=name, city=self.city)
        self.assertEqual(updated_cafe.name, name)
        self.assertEqual(updated_cafe.location, location)
        self.assertEqual(updated_cafe.image, image)

    def test_valid_update_PUT_partial(self) -> None:
        url = reverse('modify-cafe', args=[self.validCity, self.valid_cafe_name])
        name, location = 'POSTUPDATEapi', 'POSTUPDATE'
        data = {
            'name': name,
            'city': self.city.id,
            'location': location
        }

        # self.client.login(username='adminUser', password='adminpassword')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, None)

        updated_cafe = Cafe.objects.get(name=name, city=self.city)
        self.assertEqual(updated_cafe.name, name)
        self.assertEqual(updated_cafe.location, location)
        self.assertEqual(updated_cafe.image, 'image')

    def test_invalid_PUT(self) -> None:
        url = reverse('modify-cafe', args=[self.validCity, self.valid_cafe_name])
        name, location = 'POSTUPDATEapi', 'POSTUPDATE'
        data = {
            'name': name,
            'city': self.city.id,
            'location': location,
            'imagination': 12
        }

        # self.client.login(username='adminUser', password='adminpassword')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_incomplete_data_PUT(self) -> None:
        url = reverse('modify-cafe', args=[self.validCity, self.valid_cafe_name])
        data = {
            'city': self.city.id,
        }

        # self.client.login(username='adminUser', password='adminpassword')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_PATCH(self) -> None:
        url = reverse('modify-cafe', args=[self.validCity, self.valid_cafe_name])
        location = 'afterPatch'
        data = {
            'location': location
        }

        # self.client.login(username='adminUser', password='adminpassword')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        response = self.client.patch(url, data, format='json')
        cafe = Cafe.objects.get(name=self.valid_cafe_name, city=self.city)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(cafe.location, location)

    def test_unauthorized_cafe_update_PUT(self) -> None:
        url = reverse('modify-cafe', args=[self.validCity, self.valid_cafe_name])
        data = {
            'name': 'UNAUTHORIZED_UPDATE',
            'location': 'UNAUTHORIZED_LOCATION',
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_cafe_deletion(self) -> None:
        url = reverse('modify-cafe', args=[self.validCity, self.valid_cafe_name])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
