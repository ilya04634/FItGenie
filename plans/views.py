import os
import json

from django_filters.rest_framework import DjangoFilterBackend
from dotenv import load_dotenv
from drf_spectacular.types import OpenApiTypes
from openai import OpenAI
from django.conf import settings
from datetime import datetime, timedelta
from rest_framework.filters import OrderingFilter, SearchFilter

from .filters import PreferencesFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.viewsets import ModelViewSet
from .models import Preferences, Plan, Exercises, Weekly_Schedule
from .serializers import PreferencesSerializer, PlanSerializer, ExerciseSerializer, WeeklyScheduleSerializer, \
    PlanDetailSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter

load_dotenv()

client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)


class CustomPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 10


class PreferencesViewSet(ModelViewSet):
    queryset = Preferences.objects.all().order_by('id')  # Добавляем сортировку
    serializer_class = PreferencesSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['experience_level', 'age']
    pagination_class = CustomPagination  # Указываем пагинатор

    # def list(self, request, *args, **kwargs):
    #     print("GET params:", request.GET)  # Выводим параметры фильтрации
    #     queryset = self.filter_queryset(self.get_queryset())  # Применяем фильтрацию
    #     print("Filtered queryset:", queryset.query)  # Проверяем SQL-запрос
    #     return super().list(request, *args, **kwargs)


class PreferencesAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = PreferencesFilter
    ordering_fields = ['age', 'gender', 'experience_level']
    search_fields = ['goal', 'prefer_workout_ex']

    @extend_schema(
        summary="Создать предпочтения",
        description="Создаёт новый объект Preferences.",
        parameters=[
            OpenApiParameter(
                name="Authorization",
                description="Bearer access token для аутентификации",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                examples=[
                    OpenApiExample(
                        "Пример токена",
                        summary="Bearer Token",
                        value="Bearer eyJhbGciOiJIUzI1NiIsInR5..."
                    )
                ]
            )
        ],
        request=PreferencesSerializer,
        responses={
            201: OpenApiResponse(
                response=PreferencesSerializer,
                description="Объект Preferences создан успешно."
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Ошибка валидации",
                        summary="Ошибка валидации данных",
                        description="Предоставлены некорректные данные.",
                        value={"error": "Invalid data"}
                    )
                ]
            )
        },
        tags=['preferences']
    )
    def post(self, request):
        data = request.data.copy()
        data['id_user'] = request.user.id

        serializer = PreferencesSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Preferences created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Получить предпочтения",
        description="Возвращает объект Preferences по ID или список всех объектов, если ID не указан.",
        parameters=[
            OpenApiParameter(
                name="Authorization",
                description="Bearer access token для аутентификации",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                examples=[
                    OpenApiExample(
                        "Пример токена",
                        summary="Bearer Token",
                        value="Bearer eyJhbGciOiJIUzI1NiIsInR5..."
                    )
                ]
            )
        ],
        responses={
            200: OpenApiResponse(
                response=PreferencesSerializer(many=True),
                description="Успешное получение предпочтений."
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Объект не найден",
                        summary="Предпочтения не найдены",
                        description="Указанный объект предпочтений отсутствует в базе данных.",
                        value={"error": "Preferences not found"}
                    )
                ]
            )
        },
        tags=['preferences']

    )

    def get(self, request, preferences_pk=None):
        paginator = CustomPagination()
        # filterset = PreferencesFilter(request.GET, queryset=Preferences.objects.all())

        if preferences_pk:
            try:
                preferences = Preferences.objects.get(pk=preferences_pk, id_user=request.user.id)
                serializer = PreferencesSerializer(preferences)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Preferences.DoesNotExist:
                return Response({"error": "Preferences not found"}, status=status.HTTP_404_NOT_FOUND)
        # else:
        #     preferences = Preferences.objects.filter(id_user=request.user.id)
        #     paginated_preferences = paginator.paginate_queryset(preferences, request)
        #     serializer = PreferencesSerializer(paginated_preferences, many=True)
        #     return paginator.get_paginated_response(serializer.data)

        preferences = Preferences.objects.filter(id_user=request.user.id)

        # Применяем фильтрацию
        filterset = self.filterset_class(request.GET, queryset=preferences)
        if not filterset.is_valid():
            return Response({"error": "Invalid filters", "details": filterset.errors},
                            status=status.HTTP_400_BAD_REQUEST)
        filtered_preferences = filterset.qs

        paginated_preferences = paginator.paginate_queryset(filtered_preferences, request)
        serializer = PreferencesSerializer(paginated_preferences, many=True)
        return paginator.get_paginated_response(serializer.data)


    @extend_schema(
        summary="Обновить предпочтения",
        description="Обновляет объект Preferences по ID.",
        parameters=[
            OpenApiParameter(
                name="Authorization",
                description="Bearer access token для аутентификации",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                examples=[
                    OpenApiExample(
                        "Пример токена",
                        summary="Bearer Token",
                        value="Bearer eyJhbGciOiJIUzI1NiIsInR5..."
                    )
                ]
            )
        ],
        request=PreferencesSerializer,
        responses={
            200: OpenApiResponse(
                response=PreferencesSerializer,
                description="Предпочтения успешно обновлены."
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Объект не найден",
                        summary="Предпочтения не найдены",
                        description="Указанный объект предпочтений отсутствует в базе данных.",
                        value={"error": "Preferences not found"}
                    )
                ]
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Ошибка валидации",
                        summary="Некорректные данные",
                        description="Предоставлены некорректные данные для обновления предпочтений.",
                        value={"error": "Invalid data"}
                    )
                ]
            )
        },
        tags=['preferences']
    )

    def put(self, request, preferences_pk):
        try:
            preferences = Preferences.objects.get(pk=preferences_pk, id_user=request.user.id)
        except Preferences.DoesNotExist:
            return Response({"error": "Preferences not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PreferencesSerializer(preferences, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Удаление предпочтений пользователя",
        parameters=[
            OpenApiParameter(
                name="Authorization",
                description="Bearer access token для аутентификации",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                examples=[
                    OpenApiExample(
                        "Пример токена",
                        summary="Bearer Token",
                        value="eyJhbGciOiJIUzI1NiIsInR5..."
                    )
                ]
            )
        ],
        responses={
            204: OpenApiResponse(
                description="Удалено успешно.",
            ),
            404: OpenApiResponse(
                description="Объект не найден.",
                examples=[
                    OpenApiExample(
                        "Пример ошибки",
                        summary="Объект отсутствует",
                        value={"error": "Preferences not found"}
                    )
                ]
            )
        },
        tags=['preferences']
    )

    def delete(self, request, preferences_pk):
        user = request.user
        try:
            preferences = Preferences.objects.get(pk=preferences_pk, id_user=user.id)
            preferences.delete()
            return Response({"message": "Preferences deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Preferences.DoesNotExist:
            return Response({"error": "Preferences not found"}, status=status.HTTP_404_NOT_FOUND)





class GeneratePlanAPIView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        summary="Сгенерировать тренировочный план",
        description=(
            "Генерирует тренировочный план на основе предпочтений пользователя с использованием OpenAI."
        ),
        parameters=[
            OpenApiParameter(
                name="Authorization",
                description="Bearer access token для аутентификации",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                examples=[
                    OpenApiExample(
                        "Пример токена",
                        summary="Bearer Token",
                        value="eyJhbGciOiJIUzI1NiIsInR5..."
                    )
                ]
            )
        ],
        request=PreferencesSerializer,
        responses={
            201: PlanSerializer,
            400: OpenApiExample(
                "Ошибка валидации",
                value={"error": "Invalid preferences data"}
            ),
            500: OpenApiExample(
                "Ошибка сервера",
                value={"error": "OpenAI error"}
            ),
        },
        tags=['plan generation']
    )
    def post(self, request, preferences_pk):
        try:
            preferences = Preferences.objects.get(pk=preferences_pk, id_user=request.user.id)
        except Preferences.DoesNotExist:
            return Response({"error": "предпочтения не найдены"}, status=status.HTTP_404_NOT_FOUND)

        prompt = f"""
        Составь тренировочный план на русском языке в виде корректного JSON. Формат:
        {{
            "name": "string",
            "description": "string",
            "program_duration": "integer",
            "weekly_schedule": [
                {{
                    "day": "string",
                    "focus": "string",
                    "exercises": [
                        {{
                            "name": "string",
                            "sets": "string",
                            "reps": "string",
                            "rest": "string",
                            "notes": "string"
                        }}
                    ]
                }}
            ]
        }}
        Пример:
        {{
            "name": "План набора массы",
            "description": "Шестимесячная программа для набора мышечной массы.",
            "program_duration": 6,
            "weekly_schedule": [
                {{
                    "day": "Понедельник",
                    "focus": "Нижняя часть тела",
                    "exercises": [
                        {{
                            "name": "Приседания",
                            "sets": "4",
                            "reps": "6-8",
                            "rest": "2-3 минуты",
                            "notes": "Сосредоточьтесь на технике и глубине, используйте рабочий вес."
                        }}
                    ]
                }}
            ]
        }}
        Пол: {preferences.get_gender_display() or "не указан"}.
        Возраст: {preferences.age or "не указан"}.
        Рост: {preferences.height or "не указан"} см.
        Вес: {preferences.weight or "не указан"} кг.
        Уровень подготовки: {preferences.get_experience_level_display() or "не указан"}.
        Цель: {preferences.goal or "не указана"}.
        Частота тренировок: {preferences.workout_frequency or "не указана"} раза в неделю.
        Предпочтения: {preferences.prefer_workout_ex or "не указаны"}.
        Программа рассчитана на {preferences.time_of_program or "не указано"} месяцев.

        Ответ должен быть строго в формате JSON без пояснений, комментариев, текста или примеров. Только корректный JSON.
        """
        try:

            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a good sport coach with large background."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.6,
            )

            plan_dict = completion.model_dump()
            plan_text = plan_dict["choices"][0]["message"]["content"]

            cleaned_text = plan_text.replace("```json", "").strip()
            cleaned_text = cleaned_text.replace("```", "").strip()

            print(cleaned_text)

            # plan_text = completion['choices'][0]['message']['content']
            plan_data = json.loads(cleaned_text)
            print(plan_data["name"])
            print(plan_data["description"])

            plan = Plan.objects.create(
                name=plan_data["name"],
                description=plan_data["description"],
                program_duration=plan_data["program_duration"],
                id_user=request.user,
                id_preferences = Preferences.objects.get(pk=preferences_pk)
            )

            for day in plan_data["weekly_schedule"]:
                weekly_schedule = Weekly_Schedule.objects.create(
                    plan_id=plan,
                    day=day["day"],
                    focus=day["focus"]
                )

                for exercise in day["exercises"]:
                    Exercises.objects.create(
                        weekly_schedule_id=weekly_schedule,
                        name=exercise["name"],
                        sets=exercise["sets"],
                        reps=exercise["reps"],
                        rest=exercise["rest"],
                        notes=exercise["notes"]
                    )

            return Response({"plan": plan_data}, status=status.HTTP_200_OK)
            #print(plan_text)

        except json.JSONDecodeError as e:
            return Response({"error": "Ошибка парсинга JSON", "details": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": "Неизвестная ошибка", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @extend_schema(
        summary="Получить список сгенерированных планов",
        parameters=[
            OpenApiParameter(
                name="Authorization",
                description="Bearer access token для аутентификации",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                examples=[
                    OpenApiExample(
                        "Пример токена",
                        summary="Bearer Token",
                        value="eyJhbGciOiJIUzI1NiIsInR5..."
                    )
                ]
            )
        ],
        responses={
            200: PlanDetailSerializer(many=True),
        },
        tags=["plan generation"]
    )
    def get(self, request, preferences_pk=None, plan_pk=None):
        paginator = CustomPagination()

        if preferences_pk and plan_pk:
            try:
                plan = Plan.objects.get(pk=plan_pk, id_preferences_id=preferences_pk, id_user=request.user)
                serializer = PlanDetailSerializer(plan)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Plan.DoesNotExist:
                return Response({"error": "План не найден"}, status=status.HTTP_404_NOT_FOUND)

        elif preferences_pk:
            plans = Plan.objects.filter(id_preferences_id=preferences_pk, id_user=request.user)
            paginated_plans = paginator.paginate_queryset(plans, request)
            serializer = PlanDetailSerializer(paginated_plans, many=True)
            return paginator.get_paginated_response(serializer.data)

        elif plan_pk:
            plans = Plan.objects.filter(pk=plan_pk, id_user=request.user)
            paginated_plans = paginator.paginate_queryset(plans, request)
            serializer = PlanDetailSerializer(paginated_plans, many=True)
            return paginator.get_paginated_response(serializer.data)

        else:
            plans = Plan.objects.filter(id_user=request.user)
            paginated_plans = paginator.paginate_queryset(plans, request)
            serializer = PlanDetailSerializer(paginated_plans, many=True)
            return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        summary="Удалить план или все планы для предпочтений",
        description=(
                "Удаляет конкретный план по `plan_pk` и `preferences_pk`, все планы для указанных предпочтений "
                "по `preferences_pk`, или все планы, если не указан `preferences_pk` и `plan_pk`."
        ),
        parameters=[
            OpenApiParameter(
                name="Authorization",
                description="Bearer access token для аутентификации",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                examples=[
                    OpenApiExample(
                        "Пример токена",
                        summary="Bearer Token",
                        value="eyJhbGciOiJIUzI1NiIsInR5..."
                    )
                ]
            )
        ],
        request=None,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Успешное удаление плана",
                        summary="Успешное удаление",
                        description="План был успешно удалён.",
                        value={"message": "План успешно удалён"}
                    ),
                    OpenApiExample(
                        "Успешное удаление планов",
                        summary="Успешное удаление всех планов",
                        description="Все планы для указанных предпочтений были успешно удалены.",
                        value={"message": "Планы успешно удалены"}
                    )
                ]
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "План не найден",
                        summary="План не найден",
                        description="Указанный план не найден в базе данных.",
                        value={"error": "План не найден"}
                    ),
                    OpenApiExample(
                        "Планы не найдены",
                        summary="Планы не найдены",
                        description="Для указанных предпочтений планы не найдены.",
                        value={"error": "Планы для указанных предпочтений не найдены"}
                    )
                ]
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Некорректный запрос",
                        summary="Некорректный запрос",
                        description="Не указаны идентификаторы предпочтений или плана.",
                        value={"error": "Не указаны ID предпочтений или плана"}
                    )
                ]
            )
        },
        tags=['plan generation']
    )
    def delete(self, request, preferences_pk=None, plan_pk=None):
        if preferences_pk and plan_pk:
            try:
                plan = Plan.objects.get(pk=plan_pk, id_preferences_id=preferences_pk, id_user=request.user)
                plan.delete()
                return Response({"message": "План успешно удалён"}, status=status.HTTP_200_OK)
            except Plan.DoesNotExist:
                return Response({"error": "План не найден"}, status=status.HTTP_404_NOT_FOUND)

        elif preferences_pk:
            plans = Plan.objects.filter(id_preferences_id=preferences_pk, id_user=request.user)
            if plans.exists():
                plans.delete()
                return Response({"message": "Планы успешно удалены"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Планы для указанных предпочтений не найдены"},
                                status=status.HTTP_404_NOT_FOUND)

        elif plan_pk:
            try:
                plan = Plan.objects.get(pk=plan_pk, id_user=request.user)
                plan.delete()
                return Response({"message": "План успешно удалён"}, status=status.HTTP_200_OK)
            except Plan.DoesNotExist:
                return Response({"error": "План не найден"}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({"error": "Не указаны ID предпочтений или плана"}, status=status.HTTP_400_BAD_REQUEST)

    # def get(self, request):
    #     plans = Plan.objects.filter(id_user=request.user)
    #     serializer = PlanDetailSerializer(plans, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)


