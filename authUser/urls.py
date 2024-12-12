from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from drf_spectacular.utils import extend_schema
from authUser import views
from .views import RegisterView, CodeCheckVerifiedAPIView, AvatarUploadView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),  # Обновить токен
    path('register/', views.RegisterView.as_view(), name='register'),
    path('verify-email/', views.CodeCheckVerifiedAPIView.as_view(), name='CodeCheckVerified'),
    path('current-user/', views.CurrentUserView.as_view(), name='current_user'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('avatar/', AvatarUploadView.as_view(), name='upload-avatar'),

    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)