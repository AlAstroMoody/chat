from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from .views import StudentView, UserInfoView


users_urlpatterns = [
    path('trainer/', TokenObtainPairView.as_view(), name='trainer'),
    path('student/', StudentView.as_view(), name='student'),
    path('trainer/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('me/', UserInfoView.as_view(), name='user_info'),
]
