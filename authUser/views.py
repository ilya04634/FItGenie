from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Регистрация нового пользователя",
        description="Позволяет зарегистрировать нового пользователя, отправив данные через POST-запрос.",
        request=UserSerializer,  # Описание структуры запроса
        responses={
            201: OpenApiExample(
                "Успешный ответ",
                value={"message": "User created successfully"}
            ),
            400: OpenApiExample(
                "Ошибка валидации",
                value={"email": ["This field is required."]}
            )
        }
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # Создаём нового пользователя
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Получение информации о текущем пользователе",
        description="Возвращает информацию о текущем аутентифицированном пользователе.",
        responses={
            200: OpenApiExample(
                "Успешный ответ",
                value={
                    "nickname": "john_doe",
                    "email": "john.doe@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "id": 1
                }
            ),
            401: OpenApiExample(
                "Неавторизованный доступ",
                value={"detail": "Authentication credentials were not provided."}
            )
        }
    )

    def get(self, request):
        user = request.user  # Получаем текущего аутентифицированного пользователя
        return Response({
            "nickname": user.nickname,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "id": user.id
        })

    @extend_schema(
        summary="Обновление информации о пользователе",
        description="Позволяет обновить данные текущего пользователя.",
        request=UserSerializer,  # Описание структуры запроса
        responses={
            200: OpenApiExample(
                "Успешное обновление",
                value={"message": "User updated successfully"}
            ),
            400: OpenApiExample(
                "Ошибка валидации",
                value={"message": {"email": ["This field is required."]}}
            )
        }
    )

    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User updated successfully"}, status=status.HTTP_200_OK)

        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
