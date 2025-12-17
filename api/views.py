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

    #Set the user who created the BugPost
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    #Override to handle No-Authentication for list and retrieve actions
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

# BugSolutionCreate
class BugSolutionCreateView(viewsets.ModelViewSet):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = BugSolution.objects.all()
    serializer_class = serializers.BugSolutionSerializer

    #Set the user who created the BugSolution
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

# CommentCreate
class CommentCreateView(viewsets.ModelViewSet):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer

    #Set the user who created the Comment
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)