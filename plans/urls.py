from django.urls import path
from .views import PreferencesAPIView, GeneratePlanAPIView

urlpatterns = [
    path('preferences/', PreferencesAPIView.as_view(), name='preferences-list'),  # GET всех объектов и POST для создания
    path('preferences/<int:pk>/', PreferencesAPIView.as_view(), name='preferences-detail'),  # GET и PUT для конкретного объекта
    path('generated/', GeneratePlanAPIView.as_view(), name='generated-plan')
]