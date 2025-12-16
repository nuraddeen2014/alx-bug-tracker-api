from django.shortcuts import render
from . import serializers
from rest_framework import (
    generics, 
    mixins, 
    authentication, 
    permissions,
    viewsets
    )
from .models import (
    BugPost,
    BugSolution,
    Comment,
    Tag,
)

# BugPostCreate
class BugPostCreateView(viewsets.ModelViewSet):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = BugPost.objects.all()
    serializer_class = serializers.BugPostSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)