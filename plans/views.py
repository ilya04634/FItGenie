import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from django.conf import settings
from datetime import datetime, timedelta

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Preferences, Plan, Exercises, Weekly_Schedule
from .serializers import PreferencesSerializer, PlanSerializer, ExerciseSerializer, WeeklyScheduleSerializer, \
    PlanDetailSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample

load_dotenv()

client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)

class PreferencesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Создать предпочтения",
        description="Создаёт новый объект Preferences.",
        request=PreferencesSerializer,
        responses={
            201: PreferencesSerializer,
            400: OpenApiExample(
                "Ошибка валидации",
                value={"error": "Invalid data"}
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
        responses={
            200: PreferencesSerializer(many=True),
            404: OpenApiExample(
                "Объект не найден",
                value={"error": "Preferences not found"}
            ),
        },
        tags=['preferences']
    )
    def get(self, request, preferences_pk=None):
        if preferences_pk:
            try:
                preferences = Preferences.objects.get(pk=preferences_pk)
                serializer = PreferencesSerializer(preferences)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Preferences.DoesNotExist:
                return Response({"error": "Preferences not found"}, status=status.HTTP_404_NOT_FOUND)
        else:

            preferences = Preferences.objects.filter(id_user=request.user.id)
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
        responses={
            204: OpenApiExample(
                "Удалено успешно",
                value={"message": "Preference deleted successfully"}
            ),
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
                id_preferences = Preferences.objects.get(pk=plan_data["preferences"])
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
        responses={
            200: PlanDetailSerializer(many=True),
        },
        tags=["plan generation"]
    )
    def get(self, request, preferences_pk=None, plan_pk=None):
        if preferences_pk and plan_pk:
            try:
                plan = Plan.objects.get(pk=plan_pk, id_preferences_id=preferences_pk, id_user=request.user)
                serializer = PlanDetailSerializer(plan)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Plan.DoesNotExist:
                return Response({"error": "План не найден"}, status=status.HTTP_404_NOT_FOUND)

        elif preferences_pk:
            plans = Plan.objects.filter(id_preferences_id=preferences_pk, id_user=request.user)
            serializer = PlanDetailSerializer(plans, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif plan_pk:
            plans = Plan.objects.filter(pk=plan_pk, id_user=request.user)
            serializer = PlanDetailSerializer(plans, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


        else:
            plans = Plan.objects.filter(id_user=request.user)
            serializer = PlanDetailSerializer(plans, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="удалить план",
        responses={
            200: PlanDetailSerializer(many=True),
        },
        tags=["plan generation"]
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


