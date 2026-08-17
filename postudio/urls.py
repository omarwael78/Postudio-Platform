from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('follow/', views.follow, name='follow'),
    path('settings/', views.settings, name='settings'),
    path('search/', views.search, name='search'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),
    path('upload/', views.upload, name='upload'),
    path('delete-post/<uuid:post_id>/', views.delete_post, name='delete-post'),
    path('like-post/', views.like_post, name='like-post'),
    path('comment/', views.comment, name='comment'),
    path('delete-comment/<uuid:comment_id>/', views.delete_comment, name='delete-comment'),
    path('post/<uuid:post_id>/', views.post_detail, name='post-detail'),
    path('hide-post/<uuid:post_id>/', views.hide_post, name='hide-post'),
    path('repost/<uuid:post_id>/', views.repost, name='repost'),
    path('admin/', admin.site.urls),
    path('api/', include('postudio.api_urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)