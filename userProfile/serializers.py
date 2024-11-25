from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile

        fields = '__all__'


    def create(self, validated_data):#сделать валидацию
        return Profile.objects.create(**validated_data)