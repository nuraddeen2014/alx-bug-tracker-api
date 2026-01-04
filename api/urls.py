from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    BugPostCreateView,
    BugSolutionCreateView,
    CommentCreateView,
    TagCreateView,
    health,
)

# DRF-Spectacular schema and docs
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

router = DefaultRouter()
router.register(r'bug-post', BugPostCreateView)
router.register(r'bug-solution', BugSolutionCreateView)
router.register(r'comment', CommentCreateView)
router.register(r'tag', TagCreateView)

urlpatterns = [
    path('', TemplateView.as_view(template_name='api/home.html'), name='home'),
    path('health/', health, name='health'),
    path('openapi/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('api/', include(router.urls)),
]

### Push committed changes to feature origin ### Don't forget to pull the latest changes from main branch###