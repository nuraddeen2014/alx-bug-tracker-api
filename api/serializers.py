from rest_framework import serializers
from .models import (
    BugPost,
    BugSolution,
    Comment,
    Tag,
)

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('created_by',)

class BugSolutionSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = BugSolution
        fields = '__all__'
        read_only_fields = ('created_by',)

class BugPostSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    solutions = BugSolutionSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = BugPost
        fields = '__all__'
        read_only_fields = ('created_by',)
