from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from drf_spectacular.utils import extend_schema
from authUser import views
from .views import RegisterView, CodeCheckVerifiedAPIView


urlpatterns = [
    path('login/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),  # Обновить токен
    path('register/', views.RegisterView.as_view(), name='register'),
    path('verify-email/', views.CodeCheckVerifiedAPIView.as_view(), name='CodeCheckVerified'),
    path('current-user/', views.CurrentUserView.as_view(), name='current_user'),
]