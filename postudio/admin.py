from django.contrib import admin
from .models import Profile, Post, LikePost, FollowersCount, Comment, PostHide

admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(LikePost)
admin.site.register(FollowersCount)
admin.site.register(Comment)
admin.site.register(PostHide)
