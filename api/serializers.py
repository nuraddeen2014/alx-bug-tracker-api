from rest_framework import serializers
from .models import (
    BugPost,
    BugSolution,
    Comment,
    Tag,
)


class BugPostSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = BugPost
        fields = '__all__'
        read_only_fields = ('created_by',)

class BugSolutionSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = BugSolution
        fields = '__all__'
        read_only_fields = ('created_by',)

class CommentSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('created_by',)

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'