# from django.contrib.auth.models import Group, User
from rest_framework import serializers
from CaffeRatings.models import Rating, Cafe, City


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'


class CafeSerializer(serializers.ModelSerializer):
    # this mean that average_rating is not in model
    average_rating = serializers.SerializerMethodField() 

    class Meta:
        model = Cafe
        fields = ['name', 'location', 'average_rating', 'approved']

    # because average_rating is not in model but in this class we need method
    # to provide it
    def get_average_rating(self, obj):
        average = obj.average_rating
        return average


class CafeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cafe
        fields = ['name', 'image', 'location', 'city', 'approved'] # could be just '__all__'

    def validate(self, data):
        extra_fields = set(self.initial_data.keys()) - set(self.fields)
        if extra_fields:
            raise serializers.ValidationError(f'Extra fields: {', '.join(extra_fields)} are not allowed.')
        return data