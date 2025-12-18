from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    BugPostCreateView,
)

router = DefaultRouter()
router.register(r'bug-post', BugPostCreateView)

urlpatterns = [
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
     path('', include(router.urls)),
]