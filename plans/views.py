import openai
from django.conf import settings
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Preferences, Plan, User_Plan, Exercise, Exercise_Plan
from .serializers import PreferencesSerializer, PlanSerializer, ExerciseSerializer, ExercisePlanSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample


openai.api_key = settings.OPENAI_API_KEY

class PreferencesAPIView(APIView):
    """
    Обрабатывает POST, GET и PUT запросы для модели Preferences.
    """

    @extend_schema(
        summary="Создать предпочтения",
        description="Создаёт новый объект Preferences с заданными параметрами.",
        request=PreferencesSerializer,
        responses={
            201: PreferencesSerializer,
            400: OpenApiExample(
                "Ошибка валидации",
                value={"error": "Invalid data"}
            )
        },
    )
    def post(self, request):

        serializer = PreferencesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Получить предпочтения",
        description="Возвращает объект Preferences по ID или список всех объектов, если ID не указан.",
        responses={
            200: PreferencesSerializer(many=True),
            404: OpenApiExample(
                "Объект не найден",
                value={"error": "Preferences not found"}
            ),
        },
    )

    def get(self, request, pk=None):
        if pk:
            try:
                preferences = Preferences.objects.get(pk=pk)
                serializer = PreferencesSerializer(preferences)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Preferences.DoesNotExist:
                return Response({"error": "Preferences not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Возвращаем все объекты Preferences
            preferences = Preferences.objects.all()
            serializer = PreferencesSerializer(preferences, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Обновить предпочтения",
        description="Обновляет объект Preferences по ID.",
        request=PreferencesSerializer,
        responses={
            200: PreferencesSerializer,
            404: OpenApiExample(
                "Объект не найден",
                value={"error": "Preferences not found"}
            ),
            400: OpenApiExample(
                "Ошибка валидации",
                value={"error": "Invalid data"}
            )
        },
    )

    def put(self, request, pk):
        """
        Обновление объекта Preferences по его ID.
        """
        try:
            preferences = Preferences.objects.get(pk=pk)
        except Preferences.DoesNotExist:
            return Response({"error": "Preferences not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PreferencesSerializer(preferences, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GeneratePlanAPIView(APIView):
    @extend_schema(
        summary="Сгенерировать тренировочный план",
        description=(
                "Генерирует тренировочный план на основе предпочтений пользователя. "
                "Использует OpenAI для создания плана и разбивает его на упражнения."
        ),
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
    )
    def post(self, request):
        # Сериализация входных данных
        preferences_serializer = PreferencesSerializer(data=request.data)
        if preferences_serializer.is_valid():
            preferences = preferences_serializer.save()

            # Формируем запрос для OpenAI
            prompt = f"""
            Составь тренировочный план. Уровень: {preferences.get_experience_level_display()}.
            Цель: {preferences.goal}. Частота тренировок: {preferences.workout_frequency} раз в неделю.
            Предпочтения: {preferences.prefer_workout_ex}. Программа рассчитана на {preferences.time_of_program} месяцев.
            """
            try:
                # Отправляем запрос к OpenAI
                response = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=prompt,
                    max_tokens=500,
                    temperature=0.6,
                )

                plan_text = response.choices[0].text.strip()

                # Создаём объект плана
                start_date = datetime.now().date()
                end_date = start_date + timedelta(weeks=preferences.time_of_program * 4)
                plan = Plan.objects.create(
                    name="AI-Generated Plan",
                    created_by_ai=True,
                    start_date=start_date,
                    end_date=end_date,
                )

                # Разбиваем сгенерированный план на упражнения
                exercises = self.parse_plan(plan_text)
                for exercise_data in exercises:
                    exercise, _ = Exercise.objects.get_or_create(
                        name=exercise_data["name"],
                        defaults={
                            "sets": exercise_data["sets"],
                            "reps": exercise_data.get("reps"),
                            "duration": exercise_data.get("duration"),
                        },
                    )
                    # Связываем упражнения с планом
                    Exercise_Plan.objects.create(plan=plan, exercise=exercise)

                # Связываем пользователя с планом
                User_Plan.objects.create(user=preferences.id_user, plan=plan)

                # Возвращаем успешный ответ
                plan_serializer = PlanSerializer(plan)
                return Response(plan_serializer.data, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(preferences_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def parse_plan(self, plan_text):
        """
        Разбирает текст тренировочного плана, сгенерированного OpenAI, в список упражнений.
        """
        exercises = []
        for line in plan_text.split("\n"):
            if line.strip():
                parts = line.split(",")
                exercise_data = {
                    "name": parts[0].strip(),
                    "sets": int(parts[1].strip().split()[0]),
                }
                if len(parts) > 2:
                    if "reps" in parts[2]:
                        exercise_data["reps"] = int(parts[2].strip().split()[0])
                    if "minutes" in parts[2] or "seconds" in parts[2]:
                        exercise_data["duration"] = int(parts[2].strip().split()[0])
                exercises.append(exercise_data)
        return exercises


