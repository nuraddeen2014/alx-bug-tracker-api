from django.urls import path
from .views import RegisterView, login, logout, profile, UserAPIView, UserAPIDetailView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('users/me/', profile, name='profile'),
    path('users/', UserAPIView.as_view()),
    path('users/<int:pk>/', UserAPIDetailView.as_view()),
]