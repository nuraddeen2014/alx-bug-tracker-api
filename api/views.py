from django.shortcuts import render
from . import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
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
    authentication_classes = [authentication.SessionAuthentication, authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = BugPost.objects.all()
    serializer_class = serializers.BugPostSerializer

    #Set the user who created the BugPost
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    #Override to allow anonymous list/retrieve but require auth for create
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

# BugSolutionCreate
class BugSolutionCreateView(viewsets.ModelViewSet):
    authentication_classes = [authentication.SessionAuthentication, authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = BugSolution.objects.all()
    serializer_class = serializers.BugSolutionSerializer

    #Set the user who created the BugSolution
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

# CommentCreate
class CommentCreateView(viewsets.ModelViewSet):
    authentication_classes = [authentication.SessionAuthentication, authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer

    #Set the user who created the Comment
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)