from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('me/', views.CurrentUserView.as_view(), name='current_user'),
    path('posts/', views.PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<uuid:post_id>/', views.PostDetailView.as_view(), name='post-detail'),
    path('posts/<uuid:post_id>/like/', views.LikePostView.as_view(), name='like-post'),
    path('posts/<uuid:post_id>/comment/', views.CommentCreateView.as_view(), name='comment-create'),
    path('profile/<str:username>/', views.ProfileAPIView.as_view(), name='profile-api'),
    path('profile/<str:username>/follow/', views.FollowToggleView.as_view(), name='follow-toggle'),
]