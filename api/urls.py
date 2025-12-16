from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BugPostCreateView
)

router = DefaultRouter()
router.register(r'bug-post', BugPostCreateView)

urlpatterns = [
    path('', include(router.urls)),
]