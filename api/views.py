from .filters import BugPostFilter
from django.shortcuts import render, get_object_or_404
from . import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes,authentication_classes
from django.contrib.auth import authenticate, login
from rest_framework import (
    generics, 
    mixins, 
    authentication, 
    permissions,
    viewsets,
    status,
    filters,
    )
from .models import (
    BugPost,
    BugSolution,
    Comment,
    Tag,
    Upvote,
)
from .permissions import OnlyAuthorEditsOrDeletes

        
# BugPostCreate
class BugPostCreateView(viewsets.ModelViewSet):
    authentication_classes = [
        authentication.SessionAuthentication,
        authentication.TokenAuthentication
    ]
    queryset = BugPost.objects.all()
    serializer_class = serializers.BugPostSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']
    

    #Set the user who created the BugPost
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), OnlyAuthorEditsOrDeletes()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['post'])
    def add_tags(self, request, pk=None):
        post = self.get_object()

        # Only author or admin can add tags
        if request.user != post.created_by and not request.user.is_staff:
            return Response(
                {"detail": "You are not allowed to add tags to this post."},
                status=status.HTTP_403_FORBIDDEN
            )

        tag_id = request.data.get("tag")
        if not tag_id:
            return Response(
                {"detail": "Tag id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        tag = get_object_or_404(Tag, id=tag_id)

        post.tags.add(tag)
        serializer = self.get_serializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def remove_tags(self, request, pk=None):
        post = self.get_object()

        #Only author or admin removes tags
        if request.user != post.created_by and not request.user.is_staff:
            return Response({"detail":"You're not allowed to remove tags"}, status=status.HTTP_403_FORBIDDEN)
        
        tag_id = request.data.get('tag')
        
        if not tag_id:
            return Response({"detail":"Tag id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        tag = get_object_or_404(Tag, id=tag_id)
        # remove the tag from the post (fix: use post.tags.remove)
        post.tags.remove(tag)

        serializer = self.get_serializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    #create an action that maps solutions to individual bug posts
    @action(detail=True, methods=['get'])
    def solutions(self, request, pk=None):
        post = self.get_object()
        solutions = post.solutions.all()
        serializer = serializers.BugSolutionSerializer(solutions, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

# BugSolutionCreate
class BugSolutionCreateView(viewsets.ModelViewSet):
    authentication_classes = [authentication.SessionAuthentication, authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = BugSolution.objects.all()
    serializer_class = serializers.BugSolutionSerializer

    #Set the user who created the BugSolution
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    #Override to allow anonymous list/retrieve but require auth for create
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Only authenticated authors can edit/delete
            return [permissions.IsAuthenticated(), OnlyAuthorEditsOrDeletes()]
        return [permissions.IsAuthenticated()]
    
    @action(detail=True, methods=['POST'], permission_classes=[permissions.IsAuthenticated])
    def upvote(self, request, pk=None):
        solution = self.get_object()
        user = request.user

        if solution.created_by == user:
            return Response(
                {'detail': 'You cannot vote on your own solution'},
                status=status.HTTP_403_FORBIDDEN
            )

        vote, created = Upvote.objects.get_or_create(
            user=user,
            bug_solution=solution
        )

        if not created:
            # User already voted -> unvote (toggle off)
            vote.delete()
            action = 'unvoted'
            status_code = status.HTTP_200_OK
        else:
            # New vote -> toggle on
            action = 'voted'
            status_code = status.HTTP_201_CREATED

        serializer = self.get_serializer(solution)
        return Response(
            {
                'action': action,
                'solution': serializer.data
            },
            status=status_code
        )

    
# CommentCreate
class CommentCreateView(viewsets.ModelViewSet):
    authentication_classes = [authentication.SessionAuthentication, authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated,]
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer

    #Set the user who created the Comment
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    #Override to allow anonymous list/retrieve but require auth for create
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Only authenticated authors can edit/delete
            return [permissions.IsAuthenticated(), OnlyAuthorEditsOrDeletes()]
        return [permissions.IsAuthenticated()]

# TagCreate
class TagCreateView(viewsets.ModelViewSet):
    authentication_classes = [authentication.SessionAuthentication, authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated,permissions.IsAdminUser]
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    #Override to allow anonymous list/retrieve but require admin for create
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser(),]
    
