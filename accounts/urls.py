from django.urls import path
from .views import RegisterView, login, logout

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
]