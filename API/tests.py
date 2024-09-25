from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import Group
from django.db.models import Avg, IntegerField
from django.db.models.functions import Cast
from CaffeRatings.models import Cafe, Rating, MineUser, Category, City
from API.serializers import RatingSerializer, CafeSerializer


class APITest(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.create_test_data()
        self.set_auth_tokens()

    def create_test_data(self):
        # Create city and cafe
        self.city = City.objects.create(name="Test City")
        self.cafe = Cafe.objects.create(name="Test Cafe", location="123 Test St", city=self.city, image='image')

        # Create users
        self.userPassword = 'testpassword'
        self.adminPassword = 'adminpassword'
        self.coPassword = 'coupassword'
        self.user = MineUser.objects.create_user(username='testuser', password=self.userPassword)
        self.adminUser = MineUser.objects.create_user(username='adminUser', password=self.adminPassword)
        self.cafeOwnerUser = MineUser.objects.create_user(username='COUser', password=self.coPassword)

        # Assign groups
        admin_group, _ = Group.objects.get_or_create(name='admin')
        cafe_owner_group, _ = Group.objects.get_or_create(name='cafe_owner')
        self.adminUser.groups.add(admin_group)
        self.cafeOwnerUser.groups.add(cafe_owner_group)

        # Create category and rating
        self.category = Category.objects.create(name="Service")
        self.rating = Rating.objects.create(cafe=self.cafe, author=self.user, category=self.category, rating=5, icon='star')

        # Valid and invalid names
        self.valid_cafe_name = self.cafe.name
        self.invalid_cafe_name = "NonExistent Cafe"
        self.invalidCity = 'NoneExistentCity'
        self.valid_city_name = self.city.name

    def set_auth_tokens(self):
        self.basic_token = self.get_user_token(self.user, self.userPassword)
        self.admin_token = self.get_user_token(self.adminUser, self.adminPassword)
        self.co_token = self.get_user_token(self.cafeOwnerUser, self.coPassword)

    def get_user_token(self, user, password) -> str:
        url = reverse('token_obtain_pair')
        data = {'username': user.username, 'password': password}
        response = self.client.post(url, data, format='json')
        if response.status_code == status.HTTP_200_OK:
            return response.data['access']
        raise Exception('Token could not be obtained')

    def test_get_rating_valid_cafe(self):
        url = reverse('cafe-ratings', args=[self.valid_city_name, self.valid_cafe_name])
        response = self.client.get(url)
        ratings = Rating.objects.filter(cafe=self.cafe)
        serializer = RatingSerializer(ratings, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'ratings': serializer.data})

    def test_get_rating_invalid_cafe(self):
        url = reverse('cafe-ratings', args=[self.valid_city_name, self.invalid_cafe_name])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'No match for provided details')

    def test_get_rating_invalid_city(self):
        url = reverse('cafe-ratings', args=[self.invalidCity, self.invalid_cafe_name])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, f'{response.data}')
        self.assertEqual(response.data['detail'], 'No match for provided details')

    def test_get_all_existing_cafes_in_city(self):
        url = reverse('city-cafes', args=[self.valid_city_name])
        response = self.client.get(url)

        cafes = Cafe.objects.filter(city__name=self.valid_city_name).annotate(average_rating=Cast(Avg('rating__rating'), IntegerField()))
        serializer = CafeSerializer(cafes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_all_nonexisting_cafes_in_city(self):
        url = reverse('city-cafes', args=[self.invalidCity])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "No cafes found")

    def test_valid_cafe_creation(self):
        url = reverse('city-cafes', args=[self.valid_city_name])
        data = {'name': 'APICREATE', 'location': 'API TEST'}
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cafe.objects.get(name='APICREATE', city=self.city).name, 'APICREATE')

    def test_valid_cafe_creation_with_city(self):
        city = 'NOcityHERE'
        url = reverse('city-cafes', args=[city])
        data = {'name': 'APICREATE1', 'location': 'API TEST'}
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cafe.objects.get(name='APICREATE1', city=City.objects.get(name=city)).name, 'APICREATE1')
        self.assertTrue(City.objects.filter(name=city).exists(), 'Failed creating city')
        self.assertEqual(City.objects.filter(name=city).count(), 1, 'No city in database after creation')

    def test_create_duplicate(self):
        url = reverse('city-cafes', args=[self.valid_city_name])
        data = {'name': 'APICREATE3', 'location': 'API TEST'}
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        response1 = self.client.post(url, data, format='json')
        response2 = self.client.post(url, data, format='json')

        self.assertEqual(response1.status_code, status.HTTP_201_CREATED, f'Failed first creation request {response1.data}')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST, 'Failed second creation (duplication) request')

    def test_invalid_cafe_creation(self):
        url = reverse('city-cafes', args=[self.valid_city_name])
        data = {'location': 'API TEST'}
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_update_PUT_full(self):
        url = reverse('modify-cafe', args=[self.valid_city_name, self.valid_cafe_name])
        data = {
            'name': 'UPDATEapi',
            'location': 'UPDATElocation',
            'city': self.city.id,
            'image': 'UPDATEimage'
        }

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        updated_cafe = Cafe.objects.get(name=data['name'], city=self.city)
        self.assertEqual(updated_cafe.name, data['name'])
        self.assertEqual(updated_cafe.location, data['location'])
        self.assertEqual(updated_cafe.image, data['image'])

    def test_valid_update_PUT_partial(self):
        url = reverse('modify-cafe', args=[self.valid_city_name, self.valid_cafe_name])
        data = {
            'name': 'POSTUPDATEapi',
            'city': self.city.id,
            'location': 'POSTUPDATE'
        }

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        updated_cafe = Cafe.objects.get(name=data['name'], city=self.city)
        self.assertEqual(updated_cafe.location, data['location'])
        self.assertEqual(updated_cafe.image, 'image')

    def test_invalid_PUT(self):
        url = reverse('modify-cafe', args=[self.valid_city_name, self.valid_cafe_name])
        data = {
            'name': 'POSTUPDATEapi',
            'city': self.city.id,
            'location': 'POSTUPDATE',
            'imagination': 12
        }

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_incomplete_data_PUT(self):
        url = reverse('modify-cafe', args=[self.valid_city_name, self.valid_cafe_name])
        data = {'city': self.city.id}

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_PATCH(self):
        url = reverse('modify-cafe', args=[self.valid_city_name, self.valid_cafe_name])
        data = {'location': 'afterPatch'}

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.patch(url, data, format='json')
        cafe = Cafe.objects.get(name=self.valid_cafe_name, city=self.city)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(cafe.location, data['location'])

    def test_unauthorized_cafe_update_PUT(self):
        url = reverse('modify-cafe', args=[self.valid_city_name, self.valid_cafe_name])
        data = {
            'name': 'UNAUTHORIZED_UPDATE',
            'location': 'UNAUTHORIZED_LOCATION',
        }

        response = self.client.put(url, data, format='json')
        cafe = Cafe.objects.filter(name=data['name'], city__name=self.valid_city_name)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(cafe.exists())

    def test_unauthorized_cafe_deletion(self):
        url = reverse('modify-cafe', args=[self.valid_city_name, self.valid_cafe_name])
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.basic_token}')
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_cities(self):
        url = reverse('cities')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"Cities": [{"name": self.valid_city_name}]})

    def test_base_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.basic_token}')
        urlGET = reverse('cities')
        urlPUT = reverse('modify-cafe', args=[self.valid_city_name, self.valid_cafe_name])
        urlPOST = reverse('city-cafes', args=[self.valid_city_name])
        urlDELETE = reverse('modify-cafe', args=[self.valid_city_name, self.valid_cafe_name])

        # Test GET cities
        response = self.client.get(urlGET)
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'GET')
        self.assertEqual(response.data, {"Cities": [{"name": self.valid_city_name}]}, 'GET')

        # Test unauthorized PUT
        response = self.client.put(urlPUT, {'name': 'UNAUTHORIZED_UPDATE', 'location': 'UNAUTHORIZED_LOCATION'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, 'PUT')
        self.assertFalse(Cafe.objects.filter(name='UNAUTHORIZED_UPDATE', city__name=self.valid_city_name).exists(), 'PUT')

        # Test unauthorized POST
        response = self.client.post(urlPOST, {'name': 'Should', 'location': 'not work'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, 'POST')
        self.assertFalse(Cafe.objects.filter(name='Should', city__name=self.valid_city_name).exists(), 'POST')

        # Test unauthorized DELETE
        response = self.client.delete(urlDELETE)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, 'DELETE')

    def test_cafe_owner_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.co_token}')
        urlGET = reverse('cities')
        urlPUT = reverse('modify-cafe', args=[self.valid_city_name, self.valid_cafe_name])
        urlPOST = reverse('city-cafes', args=[self.valid_city_name])
        urlDELETE = reverse('modify-cafe', args=[self.valid_city_name, self.valid_cafe_name])

        # Test GET cities
        response = self.client.get(urlGET)
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'GET')
        self.assertEqual(response.data, {"Cities": [{"name": self.valid_city_name}]}, 'GET')

        # Test authorized PUT
        response = self.client.put(urlPUT, {'name': 'AUTH_UPDATE', 'location': 'AUTHORIZED_LOCATION', 'city': self.valid_city_name}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, f'PUT: {response.data}')
        self.assertTrue(Cafe.objects.filter(name='AUTH_UPDATE', city__name=self.valid_city_name).exists(), 'PUT')

        # Test authorized POST
        response = self.client.post(urlPOST, {'name': 'Should', 'location': 'work'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'POST')
        self.assertTrue(Cafe.objects.filter(name='Should', city__name=self.valid_city_name).exists(), 'POST')

        # Test unauthorized DELETE
        response = self.client.delete(urlDELETE)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, 'DELETE')

    def test_admin_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        urlGET = reverse('cities')
        urlPUT = reverse('modify-cafe', args=[self.valid_city_name, self.valid_cafe_name])
        urlPOST = reverse('city-cafes', args=[self.valid_city_name])
        name1 = 'Should'
        urlDELETE = reverse('modify-cafe', args=[self.valid_city_name, name1])

        # Test GET cities
        response = self.client.get(urlGET)
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'GET')
        self.assertEqual(response.data, {"Cities": [{"name": self.valid_city_name}]}, 'GET')

        # Test authorized PUT
        name2 = 'AUTH_UPDATE'
        response = self.client.put(urlPUT, {'name': name2, 'location': 'AUTHORIZED_LOCATION', 'city': self.valid_city_name}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, f'PUT: {response.data}')
        self.assertTrue(Cafe.objects.filter(name=name2, city__name=self.valid_city_name).exists(), 'PUT')

        # Test authorized POST
        
        response = self.client.post(urlPOST, {'name': name1, 'location': 'work'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'POST')
        self.assertTrue(Cafe.objects.filter(name=name1, city__name=self.valid_city_name).exists(), 'POST')

        # Test authorized DELETE
        response = self.client.delete(urlDELETE)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, 'DELETE')
        self.assertFalse(Cafe.objects.filter(name=name1).exists(), 'DELETE')
