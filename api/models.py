from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class BugPost(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class BugSolution(models.Model):
    description = models.TextField()
    bug_post = models.ForeignKey(BugPost,related_name='solutions' ,on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    upvotes = models.ManyToManyField(User, related_name='upvoted_posts', blank=True, null=True)

class Comment(models.Model):
    description = models.TextField()
    bug_solution = models.ForeignKey(BugSolution,related_name='comments', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    post = models.ManyToManyField(BugPost, related_name='tags', blank=True)

