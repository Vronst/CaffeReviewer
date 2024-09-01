# from django.contrib.auth.models import Group, User
from rest_framework import serializers
from CaffeRatings.models import Rating


class RatingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'
