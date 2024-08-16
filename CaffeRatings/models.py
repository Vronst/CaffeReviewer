from django.db import models
# from django.db.models import Avg
from django.contrib.auth.models import AbstractUser


# Create your models here.
class Cafe(models.Model):
    name = models.CharField(max_length=16)
    location = models.CharField(max_length=75)
    image = models.CharField(max_length=120, default=None, blank=True, null=True)

    def __str__(self):
        return f'{self.name} - {self.location}'


class Category(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return f'{self.name}'


class User(AbstractUser):
    pass


class Comments(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE)

    comment = models.CharField(max_length=500)

    def __str__(self):
        return f'{self.comment}\n-{self.author} ({self.cafe})'


class Rating(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE)

    icon = models.CharField(max_length=10)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.cafe} {self.category}{self.icon}- {self.rating}/{self.author}'
     