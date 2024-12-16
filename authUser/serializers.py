from django.contrib.auth import get_user_model
import re
from rest_framework import serializers
from .models import CustomUser
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ['nickname', 'email', 'first_name', 'last_name', 'avatar_url', 'password']

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        instance.first_name = validated_data.pop("first_name")
        instance.last_name = validated_data.pop("last_name")

        instance.save()
        return instance

    def get_avatar_url(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None


    def validate_email(self, value):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(email_regex, value):
            raise serializers.ValidationError("введен некорректный email адрес .")

        return value

    def validate_nickname(self, value):
        if len(value) >25:
            raise serializers.ValidationError("никнейм не должен содержать больше 25 символов")
        if not re.search(r'[A-Za-z]', value):
            raise serializers.ValidationError("никнейм должен содержать хотя бы 1 букву.")
        return value


    def validate_password(self, value):

        if len(value) < 8:
            raise serializers.ValidationError("пароль должен быть длинной 8 или больше символов .")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("пароль должен содержать хотя бы 1 цифру .")
        if not re.search(r'[A-Za-z]', value):
            raise serializers.ValidationError("пароль должен содержать хотя бы 1 букву.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("пароль должен содержать специальные символы.")
        return value

class EmailVerificationSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)

    def update(self, instance, validated_data):
        instance.password = validated_data.pop('password')




class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['avatar']



