from django.contrib import admin
from .models import BugPost, BugSolution, Comment, Tag

# Register your models here.
admin.site.register(BugPost)
admin.site.register(BugSolution)
admin.site.register(Comment)
admin.site.register(Tag)