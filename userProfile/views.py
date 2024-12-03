from django.shortcuts import render

# Create your views here.
from django.urls import path
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Profile
from .serializers import ProfileSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Получить профиль пользователя",
        description="Возвращает профиль текущего аутентифицированного пользователя.",
        responses={
            200: ProfileSerializer(many=True),
            401: OpenApiExample(
                "Неавторизованный доступ",
                value={"detail": "Authentication credentials were not provided."},
            ),
        },
        tags=['profile']
    )

    def get(self,request):
        profile = Profile.objects.filter(user=request.user.id)

        serializer = ProfileSerializer(profile, many=True)

        return Response({'profile': serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Создать профиль пользователя",
        description=(
                "Создаёт новый профиль для текущего аутентифицированного пользователя. "
                "Необходимо передать данные профиля в запросе."
        ),
        request=ProfileSerializer,
        responses={
            200: OpenApiExample(
                "Успешное создание",
                value={"message": "Profile created successfully!"},
            ),
            400: OpenApiExample(
                "Ошибка валидации",
                value={"message": {"field": "This field is required."}},
            ),
        },
        tags=['profile']
    )

    def post(self,request):
        dataprofile = request.data.copy()
        dataprofile['user'] = request.user.id
        serializer = ProfileSerializer(data=dataprofile)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile created successfully!'}, status=status.HTTP_200_OK)

        return Response({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)