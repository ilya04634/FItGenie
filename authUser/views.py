from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import UserSerializer, EmailVerificationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
import random

from .utils import send_verification_email


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Регистрация нового пользователя",
        description="Позволяет зарегистрировать нового пользователя, отправив данные через POST-запрос.",
        request=UserSerializer,
        responses={
            201: OpenApiExample(
                "Успешный ответ",
                value={"message": "User created successfully"}
            ),
            400: OpenApiExample(
                "Ошибка валидации",
                value={"email": ["This field is required."]}
            )
        },

        tags = ["auth"]
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            code = random.randint(100000, 999999)
            serializer.validated_data['code'] = code
            user = serializer.save()
            send_verification_email(user)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                "message": "User created successfully. A verification code has been sent to your email.",
                "access": access_token,
                "refresh": str(refresh)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CodeCheckVerifiedAPIView(APIView):
    @extend_schema(
        summary='верификация через код',
        request=EmailVerificationSerializer,
        tags=["auth"]
    )
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            entered_code = serializer.validated_data['code']
            user = request.user

            try:
                if entered_code == str(user.code):
                    if user.is_verified:
                        return Response({"message": "The verification code has already been used."},
                                        status=status.HTTP_400_BAD_REQUEST)

                    user.is_verified = True
                    user.save()

                    return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)

                return Response({"error": "Invalid code."}, status=status.HTTP_400_BAD_REQUEST)


            except CustomUser.DoesNotExist:

                return Response({"error": "Invalid code."}, status=status.HTTP_400_BAD_REQUEST)

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
        },
        tags=["auth"]
    )

    def get(self, request):
        user = request.user
        return Response({
            "nickname": user.nickname,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "id": user.id,
            "is_verified": user.is_verified
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
        },
        tags=["auth"]
    )

    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User updated successfully"}, status=status.HTTP_200_OK)

        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="удаление пользователя",
        tags=["auth"]
    )

    def delete(self, request):

        user = request.user

        user.delete()
        return Response({"message": "User updated successfully"}, status=status.HTTP_200_OK)




