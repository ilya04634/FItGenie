from django.urls import path
from .views import PreferencesAPIView, GeneratePlanAPIView

urlpatterns = [
    path('preferences/', PreferencesAPIView.as_view(), name='preferences-list'),
    path('preferences/<int:preferences_pk>/info/', PreferencesAPIView.as_view(), name='preferences-detail'),
    path('preferences/<int:preferences_pk>/plan/', GeneratePlanAPIView.as_view(), name='preferences|generate-plan-list'),
    path('preferences/<int:preferences_pk>/plan/<int:plan_pk>/info/', GeneratePlanAPIView.as_view(),
         name='preferences|generate-plan-detail'),
    path('plan/', GeneratePlanAPIView.as_view(), name='generate-plan-list'),
    path('plan/<int:plan_pk>/info/', GeneratePlanAPIView.as_view(), name='generate-plan-detail'),

]