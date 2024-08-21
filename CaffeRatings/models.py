from django.db import models
# from django.db.models import Avg
from django.contrib.auth.models import AbstractUser
# TODO: create user manager? make it register and login c;
# TODO: email verification


# Create your models here.
class City(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Unique city names

    def __str__(self):
        return self.name


class Cafe(models.Model):
    name = models.CharField(max_length=16, unique=False)
    location = models.CharField(max_length=75)
    image = models.CharField(max_length=120, default=None, blank=True, null=True)
    city = models.ForeignKey(City, related_name='cafes', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} - {self.location}'


class Category(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return f'{self.name}'


class MineUser(AbstractUser):
    pass


class Comments(models.Model):
    author = models.ForeignKey(MineUser, on_delete=models.CASCADE)
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE)

    comment = models.CharField(max_length=500)

    def __str__(self):
        return f'{self.comment}\n-{self.author} ({self.cafe})'


class Rating(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.ForeignKey(MineUser, on_delete=models.CASCADE)
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE)

    icon = models.CharField(max_length=10)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.cafe} {self.category}{self.icon}- {self.rating}/{self.author}'
     