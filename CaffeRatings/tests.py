from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import *


class OverallTestCase(TestCase):
    def setUp(self):
        self.city1 = City.objects.create(name='Test City')
        self.city2 = City.objects.create(name='Test City 2')

        # Create cafes associated with cities
        Cafe.objects.create(name='Test cafe', location='testing suite', image='test_image_1.jpg', city=self.city1, approved=True)
        Cafe.objects.create(name='Test 2 cafe 2', location='testing 2 suite 2', image='test_image_2.jpg', city=self.city2, approved=True)
        Cafe.objects.create(name='Test 3 cafe 3', location='testing 3 suite 3', image='test', city=self.city2, approved=True)

        Category.objects.create(name='CatTest')
        Category.objects.create(name='CatTest2')

        self.User = get_user_model()

    def test_location(self):
        cafe1 = Cafe.objects.get(name='Test cafe')
        cafe2 = Cafe.objects.get(name='Test 2 cafe 2')
        self.assertEqual(cafe1.location, 'testing suite')
        self.assertEqual(cafe2.location, 'testing 2 suite 2')

    def test_category(self):
        category1 = Category.objects.get(name='CatTest')
        category2 = Category.objects.get(name='CatTest2')
        self.assertEqual(category1.name, 'CatTest')
        self.assertEqual(category2.name, 'CatTest2')

    def test_create_user(self):
        user = self.User.objects.create_user(
            username='testuser',
            password='securepassword',
            email='testuser@example.com'
        )
        # Verify user attributes
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertTrue(user.check_password('securepassword'))
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

    def test_create_superuser(self):
        superuser = self.User.objects.create_superuser(
            username='superuser',
            password='superpassword',
            email='superuser@example.com'
        )
        # Verify superuser attributes
        self.assertEqual(superuser.username, 'superuser')
        self.assertEqual(superuser.email, 'superuser@example.com')
        self.assertTrue(superuser.check_password('superpassword'))
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)

    def test_create_comment(self):
        user = self.User.objects.create_user(
            username='commentuser',
            password='securepassword',
            email='commentuser@example.com'
        )
        cafe = Cafe.objects.get(name='Test cafe')
        comment = Comments.objects.create(
            author=user,
            cafe=cafe,
            comment='This is a test comment.'
        )
        # Verify comment attributes
        self.assertEqual(comment.author, user)
        self.assertEqual(comment.cafe, cafe)
        self.assertEqual(comment.comment, 'This is a test comment.')

    def test_create_rating(self):
        user = self.User.objects.create_user(
            username='ratinguser',
            password='securepassword',
            email='ratinguser@example.com'
        )
        cafe = Cafe.objects.get(name='Test 2 cafe 2')
        category = Category.objects.get(name='CatTest')
        rating = Rating.objects.create(
            category=category,
            author=user,
            cafe=cafe,
            icon='star',
            rating=5
        )
        # Verify rating attributes
        self.assertEqual(rating.category, category)
        self.assertEqual(rating.author, user)
        self.assertEqual(rating.cafe, cafe)
        self.assertEqual(rating.icon, 'star')
        self.assertEqual(rating.rating, 5)
    
    def test_city_and_cafe(self):
        # Verify city and associated cafes
        city1_cafes = self.city1.cafes.all()  # Using related_name 'cafes'
        city2_cafes = self.city2.cafes.all()
        

        self.assertEqual(city1_cafes.count(), 1)  # Should be one cafe in city1
        self.assertEqual(city2_cafes.count(), 2)  # Should be two cafes in city2

        cafe1 = Cafe.objects.get(name='Test cafe')
        cafe2 = Cafe.objects.get(name='Test 2 cafe 2')
        cafe3 = Cafe.objects.get(name='Test 3 cafe 3')

        self.assertEqual(cafe1.city, self.city1)
        self.assertEqual(cafe2.city, self.city2)
        self.assertEqual(cafe3.city, self.city2)

    def test_cafe_listing(self):

        response = self.client.get(reverse('city', args=['Test City 2']))

        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, 'Test 2 cafe 2')
        self.assertContains(response, 'Test 3 cafe 3')

        self.assertNotContains(response, 'Test cafe')
        self.assertNotContains(response, 'Non-exisitent Cafe')

        response = self.client.get(reverse('city', args=['Test City']))

        self.assertContains(response, 'Test cafe')

        self.assertNotContains(response, 'Test 2 cafe 2')
        self.assertNotContains(response, 'Test 3 cafe 3')

