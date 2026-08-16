import random
import shutil
import os
from django.postudio.management.base import BaseCommand
from django.contrib.auth.models import User
from postudio.models import Profile, Post, FollowersCount, LikePost
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

demo_users = [
    {'username': 'john_doe', 'email': 'john@example.com', 'password': 'test12345', 'bio': 'Photographer & traveler', 'location': 'New York, USA'},
    {'username': 'jane_smith', 'email': 'jane@example.com', 'password': 'test12345', 'bio': 'Digital artist | Coffee lover', 'location': 'London, UK'},
    {'username': 'alex_chen', 'email': 'alex@example.com', 'password': 'test12345', 'bio': 'Software developer by day, gamer by night', 'location': 'San Francisco, USA'},
    {'username': 'sarah_lee', 'email': 'sarah@example.com', 'password': 'test12345', 'bio': 'Fitness enthusiast & foodie', 'location': 'Seoul, South Korea'},
    {'username': 'mike_wilson', 'email': 'mike@example.com', 'password': 'test12345', 'bio': 'Music producer | vinyl collector', 'location': 'Austin, USA'},
    {'username': 'emma_davis', 'email': 'emma@example.com', 'password': 'test12345', 'bio': 'Fashion blogger & content creator', 'location': 'Paris, France'},
]

post_captions = [
    "Beautiful sunset today! Nature never fails to amaze me.",
    "Just finished reading this amazing book. Highly recommend!",
    "Weekend vibes with good friends and great food.",
    "New project coming soon! Stay tuned.",
    "Morning coffee and good music. Perfect start to the day.",
    "Throwback to that amazing trip last summer.",
    "Grateful for all the support. Love you guys!",
    "Trying out a new recipe today. Wish me luck!",
    "City lights always make me feel alive.",
    "Hard work pays off. Never give up on your dreams.",
    "Beach day! Nothing beats the ocean breeze.",
    "New addition to the family! Meet my new best friend.",
    "Art exhibition was incredible today. So inspired.",
    "Fitness journey update: 3 months in and feeling great!",
    "Late night coding session. The struggle is real.",
]

class Command(BaseCommand):
    help = 'Seeds the database with demo users, posts, and social connections'

    def copy_sample_image(self, src_name, dest_name):
        src = os.path.join(settings.STATICFILES_DIRS[0], 'assets', 'images', 'post', src_name)
        dest = os.path.join(settings.MEDIA_ROOT, 'post_images', dest_name)
        if os.path.exists(src) and not os.path.exists(dest):
            shutil.copy2(src, dest)
            return True
        return False

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        created_users = []
        for i, user_data in enumerate(demo_users):
            if User.objects.filter(username=user_data['username']).exists():
                self.stdout.write(f"  User {user_data['username']} already exists, skipping")
                user = User.objects.get(username=user_data['username'])
            else:
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                )
                self.stdout.write(f"  Created user: {user_data['username']}")

            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'id_user': user.id,
                    'bio': user_data['bio'],
                    'location': user_data['location'],
                }
            )
            if not created:
                profile.bio = user_data['bio']
                profile.location = user_data['location']
                profile.save()

            created_users.append(user)

        seed_media_dir = os.path.join(settings.MEDIA_ROOT, 'post_images')
        os.makedirs(seed_media_dir, exist_ok=True)

        sample_ids = [10, 20, 25, 30, 36, 42, 48, 55, 60, 65, 68, 74, 82, 91, 96, 99, 100, 101, 102, 103, 104, 106, 110, 112, 114, 116, 118, 120, 121, 122, 123, 124, 125, 128, 130, 132, 134, 136, 138, 140]
        post_images = [f'sample_{sid}.jpg' for sid in sample_ids]

        for user in created_users:
            num_posts = random.randint(3, 6)
            chosen = random.sample(post_images, num_posts)
            for j, img_name in enumerate(chosen):
                dest_name = f"{user.username}_{j}_{img_name}"
                src = os.path.join(seed_media_dir, img_name)
                dest = os.path.join(seed_media_dir, dest_name)
                if os.path.exists(src) and not os.path.exists(dest):
                    shutil.copy2(src, dest)

                caption = random.choice(post_captions)
                hours_ago = random.randint(1, 720)
                created_at = timezone.now() - timedelta(hours=hours_ago)

                Post.objects.get_or_create(
                    user=user.username,
                    image=f'post_images/{dest_name}',
                    defaults={
                        'caption': caption,
                        'created_at': created_at,
                        'no_of_likes': random.randint(0, 50),
                    }
                )
            self.stdout.write(f"  Created {num_posts} posts for: {user.username}")

        for user in created_users:
            potential_follows = [u for u in created_users if u != user]
            to_follow = random.sample(potential_follows, random.randint(1, min(3, len(potential_follows))))
            for follow_user in to_follow:
                FollowersCount.objects.get_or_create(
                    follower=user.username,
                    user=follow_user.username,
                )

        for post in Post.objects.all():
            likers = random.sample(created_users, random.randint(1, min(4, len(created_users))))
            for liker in likers:
                LikePost.objects.get_or_create(
                    post_id=post.id,
                    username=liker.username,
                )
            post.no_of_likes = LikePost.objects.filter(post_id=post.id).count()
            post.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {len(created_users)} users with posts and connections!'))
        self.stdout.write(self.style.SUCCESS('Demo login credentials:'))
        self.stdout.write(f'  Username: {demo_users[0]["username"]}  Password: {demo_users[0]["password"]}')
        self.stdout.write(f'  Or any of the {len(demo_users)} demo users above with password: test12345')
