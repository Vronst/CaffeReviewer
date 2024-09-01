# from django.contrib.auth.models import Group, User
from rest_framework import serializers
from CaffeRatings.models import Rating, Cafe


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'


class CafeSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Cafe
        fields = ['name', 'location', 'average_rating']

    def get_average_rating(self, obj):
        average = obj.average_rating
        return average

