from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Profile, Post, LikePost, FollowersCount, Comment, PostHide
from itertools import chain
import random
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from datetime import date, timedelta
from collections import defaultdict
import mimetypes
from .serializers import UserSerializer, ProfileSerializer, PostSerializer, CommentSerializer

# Create your views here.

def get_streak_color(day_count):
    if day_count <= 10:
        return '#3B82F6'
    elif day_count <= 20:
        return '#F59E0B'
    elif day_count <= 30:
        return '#F97316'
    elif day_count <= 50:
        return '#EF4444'
    else:
        return '#8B5CF6'

def compute_post_streaks(posts):
    streaks = {}
    user_dates = defaultdict(list)
    for p in posts:
        user_dates[p.user].append(p.created_at.date())
    for user, dates in user_dates.items():
        unique_dates = sorted(set(dates), reverse=True)
        streak_map = {}
        for d in unique_dates:
            count = 1
            check = d - timedelta(days=1)
            while check in unique_dates:
                count += 1
                check -= timedelta(days=1)
            streak_map[d] = count
        for p in posts:
            if p.user == user:
                streaks[str(p.id)] = streak_map.get(p.created_at.date(), 1)
    return streaks

@login_required(login_url='signin')
def index(request):
    from django.shortcuts import get_object_or_404
    user_object = User.objects.get(username=request.user.username)
    user_profile, created = Profile.objects.get_or_create(user=user_object, defaults={'id_user': user_object.id})

    user_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)

    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))

    if not feed_list:
        all_posts = Post.objects.all().order_by('-created_at')[:20]
        feed_list = list(all_posts)

    # exclude hidden posts
    hidden_ids = PostHide.objects.filter(user=request.user.username).values_list('post_id', flat=True)
    feed_list = [p for p in feed_list if str(p.id) not in hidden_ids]

    # user suggestion starts
    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)
    
    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in list(new_suggestions_list) if ( x not in list(current_user))]
    random.shuffle(final_suggestions_list)

    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))

    post_streaks = compute_post_streaks(feed_list)
    for p in feed_list:
        p_id = str(p.id)
        p.post_day = post_streaks.get(p_id, 1)
        p.streak_color = get_streak_color(p.post_day)

    return render(request, 'index.html', {'user_profile': user_profile, 'posts':feed_list, 'suggestions_username_profile_list': suggestions_username_profile_list[:4]})

@login_required(login_url='signin')
def delete_post(request, post_id):
    post = Post.objects.filter(id=post_id, user=request.user.username).first()
    if post:
        post.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Post not found'}, status=404)

@login_required(login_url='signin')
def hide_post(request, post_id):
    username = request.user.username
    existing = PostHide.objects.filter(user=username, post_id=post_id).first()
    if existing:
        existing.delete()
        return JsonResponse({'success': True, 'hidden': False, 'msg': 'Post unhidden'})
    PostHide.objects.create(user=username, post_id=post_id)
    return JsonResponse({'success': True, 'hidden': True, 'msg': 'Post hidden from your feed'})

@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        caption = request.POST.get('caption', '')
        post_type = request.POST.get('post_type', 'image')
        uploaded_file = request.FILES.get('image_upload')

        def is_image(f):
            if not f:
                return False
            ct, _ = mimetypes.guess_type(f.name)
            return ct and ct.startswith('image/')

        if post_type == 'text':
            new_post = Post.objects.create(user=user, post_type='text', caption=caption)
            new_post.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'post_id': str(new_post.id)})
            return redirect('/')

        else:
            if not uploaded_file:
                messages.error(request, 'Please select an image to upload')
                return redirect('/')
            if not is_image(uploaded_file):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'error': 'Only image files are allowed (jpg, png, etc.)'}, status=400)
                messages.error(request, 'Only image files are allowed')
                return redirect('/')
            new_post = Post.objects.create(user=user, post_type='image', image=uploaded_file, caption=caption)
            new_post.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'post_id': str(new_post.id)})
            return redirect('/')
    else:
        return redirect('/')

@login_required(login_url='signin')
def search(request):
    from django.shortcuts import get_object_or_404
    user_object = User.objects.get(username=request.user.username)
    user_profile, created = Profile.objects.get_or_create(user=user_object, defaults={'id_user': user_object.id})

    username_profile_list = []

    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []

        for users in username_object:
            username_profile.append(users.id)

        profile_lists = []
        for ids in username_profile:
            profile_lists.append(Profile.objects.filter(id_user=ids))
        
        username_profile_list = list(chain(*profile_lists))
    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})

@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    liked = False
    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes += 1
        post.save()
        liked = True
    else:
        like_filter.delete()
        post.no_of_likes -= 1
        post.save()
        liked = False

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'no_of_likes': post.no_of_likes})

    return redirect('/')

@login_required(login_url='signin')
def comment(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        text = request.POST.get('text', '').strip()

        if not post_id or not text:
            return JsonResponse({'error': 'Missing post_id or text'}, status=400)

        post = Post.objects.filter(id=post_id).first()
        if not post:
            return JsonResponse({'error': 'Post not found'}, status=404)

        new_comment = Comment.objects.create(post=post, user=request.user.username, text=text)
        new_comment.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'id': str(new_comment.id),
                'user': new_comment.user,
                'text': new_comment.text,
                'created_at': new_comment.created_at.strftime('%b %d, %Y'),
            })

        return redirect('/')
    return redirect('/')

@login_required(login_url='signin')
def delete_comment(request, comment_id):
    comment = Comment.objects.filter(id=comment_id, user=request.user.username).first()
    if comment:
        comment.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Comment not found'}, status=404)

@login_required(login_url='signin')
def repost(request, post_id):
    original = Post.objects.filter(id=post_id).first()
    if not original:
        return JsonResponse({'error': 'Post not found'}, status=404)

    username = request.user.username

    existing = Post.objects.filter(user=username, caption=f'Reposted from @{original.user} (post:{post_id})').first()
    if existing:
        existing.delete()
        return JsonResponse({'success': True, 'action': 'unreposted'})

    from django.core.files.base import ContentFile
    import urllib.request

    try:
        new_post = Post(user=username, post_type=original.post_type, caption=f'Reposted from @{original.user} (post:{post_id})')
        if original.image:
            img_url = request.build_absolute_uri(original.image.url)
            img_data = urllib.request.urlopen(img_url, timeout=10).read()
            new_post.image.save(original.image.name.split('/')[-1], ContentFile(img_data), save=True)
        else:
            new_post.save()
        return JsonResponse({'success': True, 'action': 'reposted'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required(login_url='signin')
def post_detail(request, post_id):
    post = Post.objects.filter(id=post_id).first()
    if not post:
        return JsonResponse({'error': 'Post not found'}, status=404)

    comments = []
    for c in post.comments.all().order_by('-created_at')[:10]:
        comments.append({
            'id': str(c.id),
            'user': c.user,
            'text': c.text,
            'created_at': c.created_at.strftime('%b %d, %Y'),
        })

    return JsonResponse({
        'id': str(post.id),
        'user': post.user,
        'post_type': post.post_type,
        'image': post.image.url if post.image else '',
        'caption': post.caption,
        'created_at': post.created_at.strftime('%b %d, %Y'),
        'no_of_likes': post.no_of_likes,
        'comments': comments,
    })

@login_required(login_url='signin')
def profile(request, username):
    from django.shortcuts import get_object_or_404
    user_object = User.objects.get(username=username)
    user_profile, created = Profile.objects.get_or_create(user=user_object, defaults={'id_user': user_object.id})
    user_posts = Post.objects.filter(user=username)
    # exclude posts hidden by the current viewer (only when viewing someone else's profile)
    if username != request.user.username:
        hidden_ids = PostHide.objects.filter(user=request.user.username).values_list('post_id', flat=True)
        user_posts = [p for p in user_posts if str(p.id) not in hidden_ids]
    user_post_length = len(user_posts)

    follower = request.user.username
    user = username

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    user_followers = len(FollowersCount.objects.filter(user=username))
    user_following = len(FollowersCount.objects.filter(follower=username))

    current_user_profile, created = Profile.objects.get_or_create(user=request.user, defaults={'id_user': request.user.id})

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
        'current_user_profile': current_user_profile,
    }
    return render(request, 'profile.html', context)

@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+user)
    else:
        return redirect('/')

@login_required(login_url='signin')
def settings(request):
    user_profile, _ = Profile.objects.get_or_create(user=request.user, defaults={'id_user': request.user.id})
    password_changed = False

    if request.method == 'POST':
        if 'bio' in request.POST:
            if request.FILES.get('image') == None:
                image = user_profile.profileimg
                bio = request.POST['bio']
                location = request.POST['location']
                user_profile.profileimg = image
                user_profile.bio = bio
                user_profile.location = location
                user_profile.save()
            if request.FILES.get('image') != None:
                image = request.FILES.get('image')
                bio = request.POST['bio']
                location = request.POST['location']
                user_profile.profileimg = image
                user_profile.bio = bio
                user_profile.location = location
                user_profile.save()
            return redirect('settings')
        elif 'old_password' in request.POST:
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully!')
                return redirect('settings')
            else:
                for error in form.errors.values():
                    messages.error(request, error)

    return render(request, 'setting.html', {'user_profile': user_profile})

def signup(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                #log user in and redirect to settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                #create a Profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Password Not Matching')
            return redirect('signup')
        
    else:
        return render(request, 'signup.html')

@ensure_csrf_cookie
def signin(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')

    else:
        return render(request, 'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

def error_404(request, exception):
    return render(request, '404.html', status=404)

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, many=False)
        return Response(serializer.data)

class PostListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        posts = Post.objects.all().order_by('-created_at')[:20]
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user.username)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
            serializer = PostSerializer(post, many=False)
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

class LikePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = Post.objects.get(id=post_id)
        like_filter = LikePost.objects.filter(post_id=post_id, username=request.user.username).first()

        liked = False
        if like_filter is None:
            LikePost.objects.create(post_id=post_id, username=request.user.username)
            post.no_of_likes += 1
            post.save()
            liked = True
        else:
            like_filter.delete()
            post.no_of_likes -= 1
            post.save()
            liked = False

        return Response({'liked': liked, 'no_of_likes': post.no_of_likes})

class CommentCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = Post.objects.get(id=post_id)
        text = request.data.get('text', '').strip()

        if not text:
            return Response({'error': 'Text is required'}, status=status.HTTP_400_BAD_REQUEST)

        new_comment = Comment.objects.create(post=post, user=request.user.username, text=text)
        serializer = CommentSerializer(new_comment, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
            profile = Profile.objects.get(user=user)
            serializer = ProfileSerializer(profile, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

class FollowToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, username):
        user = request.user.username
        target_user = username

        if FollowersCount.objects.filter(follower=user, user=target_user).first():
            FollowersCount.objects.get(follower=user, user=target_user).delete()
            return Response({'following': False})
        else:
            FollowersCount.objects.create(follower=user, user=target_user)
            return Response({'following': True})