# from django.contrib.auth.models import Group, User
from typing import Dict, Any, Type
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken
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
    def get_average_rating(self, obj: Cafe) -> float:
        average = obj.average_rating
        return average


class CafeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cafe
        fields = ['name', 'image', 'location', 'city', 'approved'] # could be just '__all__'

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        extra_fields = set(self.initial_data.keys()) - set(self.fields)
        if extra_fields:
            raise serializers.ValidationError(f'Extra fields: {', '.join(extra_fields)} are not allowed.')
        return data
    

class GroupBasedTokenObtainPairSerializer(TokenObtainPairSerializer):    
    @classmethod
    def get_token(cls: Type[TokenObtainPairSerializer], user: User) -> Type[RefreshToken]:
        token = super().get_token(user)

        if user.groups.filter(name='admin').exists(): 
            token['custom_token_type'] = 'admin'
        elif user.groups.filter(name='cafe_owner').exists():
            token['custom_token_type'] = 'cafe_owner'
        else:
            token['custom_token_type'] = 'basic'

        return token

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['name']   
