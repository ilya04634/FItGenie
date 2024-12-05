import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from django.conf import settings
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Preferences, Plan, Exercises, Weekly_Schedule
from .serializers import PreferencesSerializer, PlanSerializer, ExerciseSerializer, WeeklyScheduleSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample

load_dotenv()

client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)

class PreferencesAPIView(APIView):


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

        data = request.data.copy()  # Копируем данные запроса
        data['user'] = request.user.id

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
        tags=['preferences']
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

            preferences = Preferences.objects.filter(user=request.user)
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

    def put(self, request, pk):
        try:
            preferences = Preferences.objects.get(pk=pk, user=request.user)
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

    def delete(self, request, pk):
        user = request.user
        try:
            preferences = Preferences.objects.get(pk=pk, user=user)
            preferences.delete()
            return Response({"message": "Preferences deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Preferences.DoesNotExist:
            return Response({"error": "Preferences not found"}, status=status.HTTP_404_NOT_FOUND)



class GeneratePlanAPIView(APIView):
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
    def post(self, request):
        preferences_serializer = PreferencesSerializer(data=request.data)
        if preferences_serializer.is_valid():
            preferences = preferences_serializer.save()


            prompt = f"""
            Составь тренировочный план в виде корректного JSON. Формат:
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
                "name": "Mass Gain Plan",
                "description": "A 6-month program focused on gaining muscle mass.",
                "program_duration": 6,
                "weekly_schedule": [
                    {{
                        "day": "Monday",
                        "focus": "Lower Body",
                        "exercises": [
                            {{
                                "name": "Squats",
                                "sets": "4",
                                "reps": "6-8",
                                "rest": "2-3 minutes",
                                "notes": "Focus on depth and form, use a weight that challenges you."
                            }}
                        ]
                    }}
                ]
            }}
            Уровень: {preferences.get_experience_level_display()}.
            Цель: {preferences.goal}. Частота тренировок: {preferences.workout_frequency} раз в неделю.
            Предпочтения: {preferences.prefer_workout_ex}. Программа рассчитана на {preferences.time_of_program} месяцев.
            Верни только JSON без пояснений, комментариев или текста.
            """
            try:

                completion = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.6,
                )

                plan_dict = completion.model_dump()
                plan_text = plan_dict["choices"][0]["message"]["content"]

                cleaned_text = plan_text.replace("```json", "").strip()
                cleaned_text = cleaned_text.replace("```", "").strip()

                print(plan_text)

                # plan_text = completion['choices'][0]['message']['content']
                plan_data = json.loads(cleaned_text)
                print(plan_data["name"])
                print(plan_data["description"])

                plan = Plan.objects.create(
                    name=plan_data["name"],
                    description=plan_data["description"],
                    program_duration=plan_data["program_duration"]
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

                #  "weekly_schedule": [
                #     {{
                #         "day": "string",
                #         "focus": "string",
                #         "exercises": [
                #             {{
                #                 "name": "string",
                #                 "sets": "string",
                #                 "reps": "string",
                #                 "rest": "string",
                #                 "notes": "string"
                #             }}
                #         ]
                #     }}
                # ]

                # Получить id плана

                # for day in plan_data["weekly_schedule"]:
                #     # Создаешь сущность в таблице расписания, сохраняешь id
                #
                #     for exercise in day["exercises"]:
                #
                #         # Добавляю управжнение в базу данныех, добавляешь имя упражнения в exercisesNames




                return Response({"plan": plan_data}, status=status.HTTP_200_OK)
                #print(plan_text)

            except json.JSONDecodeError as e:
                print(f"ошибка парсинга JSON")


                # plan_serializer = PlanSerializer(data=plan_data)
                # if plan_serializer.is_valid():
                #     plan_serializer.save()
                #     return Response(plan_serializer.data, status=status.HTTP_201_CREATED)
                # else:
                #     return Response(plan_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(preferences_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
