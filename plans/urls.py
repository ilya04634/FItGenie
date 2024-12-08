from django.urls import path
from .views import PreferencesAPIView, GeneratePlanAPIView

urlpatterns = [
    path('preferences/', PreferencesAPIView.as_view(), name='preferences-list'),
    path('preferences/<int:pk>/', PreferencesAPIView.as_view(), name='preferences-detail'),
    path('generated/', GeneratePlanAPIView.as_view(), name='generated-plans_list'),
    path('generated/<int:pk>/', GeneratePlanAPIView.as_view(), name='generated-plan-detail'),
]