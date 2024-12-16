import django_filters
from .models import Preferences


class PreferencesFilter(django_filters.FilterSet):

    age = django_filters.NumberFilter(field_name='age')
    goal = django_filters.CharFilter(field_name='goal')
    experience_level = django_filters.CharFilter(field_name='experience_level')
    gender = django_filters.CharFilter(field_name='gender')
    prefer_workout_ex = django_filters.CharFilter(field_name='prefer_workout_ex')

    class Meta:
        model = Preferences
        fields = ['age','goal', 'experience_level', 'gender']