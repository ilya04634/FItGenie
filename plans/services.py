# import openai
# from django.conf import settings
#
# openai.api_key = settings.OPENAI_API_KEY
#
#
# def generate_workout_plan(preferences):
#
#     prompt = (
#         f"Создай тренировочный план для пользователя в формате JSON. "
#         f"Цель: {preferences['goal']}. "
#         f"Уровень подготовки: {preferences['experience_level']}. "
#         f"Частота тренировок: {preferences['workout_frequency']} раз в неделю. "
#         f"Длительность программы: {preferences['time_of_program']} месяцев. "
#         f"Предпочитаемые упражнения: {preferences['prefer_workout_ex']}."
#     )
#
#     try:
#         response = openai.Completion.create(
#             # model="text-davinci-003",
#             model="text-curie-001",
#             prompt=prompt,
#             max_tokens=500,
#             temperature=0.6,
#         )
#         return response.choices[0].text.strip()
#     except Exception as e:
#         return f"Ошибка генерации плана: {str(e)}"