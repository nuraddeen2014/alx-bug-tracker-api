from rest_framework import serializers
from .models import (
    BugPost,
    BugSolution,
    Comment,
    Tag,
)


class BugPostSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BugPost
        fields = '__all__'

        read_only_fields = ('created_by',)

class BugSolutionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BugSolution
        fields = '__all__'

class CommentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'