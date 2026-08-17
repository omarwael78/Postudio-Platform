import random
import shutil
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from postudio.models import Profile, Post, FollowersCount, LikePost, Comment
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

demo_users = [
    {'username': 'john_doe', 'email': 'john@example.com', 'password': 'test12345', 'bio': 'Photographer & traveler. Capturing moments around the globe.', 'location': 'New York, USA'},
    {'username': 'jane_smith', 'email': 'jane@example.com', 'password': 'test12345', 'bio': 'Digital artist | Coffee lover | Creating one pixel at a time', 'location': 'London, UK'},
    {'username': 'alex_chen', 'email': 'alex@example.com', 'password': 'test12345', 'bio': 'Software developer by day, gamer by night. Building the future.', 'location': 'San Francisco, USA'},
    {'username': 'sarah_lee', 'email': 'sarah@example.com', 'password': 'test12345', 'bio': 'Fitness enthusiast & foodie. Life is better when you sweat.', 'location': 'Seoul, South Korea'},
    {'username': 'mike_wilson', 'email': 'mike@example.com', 'password': 'test12345', 'bio': 'Music producer | vinyl collector | Sound is my therapy', 'location': 'Austin, USA'},
    {'username': 'emma_davis', 'email': 'emma@example.com', 'password': 'test12345', 'bio': 'Fashion blogger & content creator. Style is a way to say who you are.', 'location': 'Paris, France'},
    {'username': 'omar_wael', 'email': 'omar@example.com', 'password': 'test12345', 'bio': 'Full-stack developer & tech enthusiast. Turning ideas into code.', 'location': 'Cairo, Egypt'},
    {'username': 'lisa_ray', 'email': 'lisa@example.com', 'password': 'test12345', 'bio': 'Travel blogger. The world is my playground.', 'location': 'Sydney, Australia'},
]

image_captions = [
    "Beautiful sunset today! Nature never fails to amaze me.",
    "Weekend vibes with good friends and great food.",
    "New project coming soon! Stay tuned.",
    "Throwback to that amazing trip last summer.",
    "Grateful for all the support. Love you guys!",
    "City lights always make me feel alive.",
    "Beach day! Nothing beats the ocean breeze.",
    "Art exhibition was incredible today. So inspired.",
    "Morning coffee and good music. Perfect start to the day.",
    "Exploring new places, making new memories.",
    "Golden hour never disappoints.",
    "The mountains are calling and I must go.",
    "Street food adventures in the city.",
    "Studio sessions all night. New music loading.",
    "Architecture is frozen music.",
]

text_captions = [
    "Just finished reading an incredible book. Highly recommend it to anyone looking for inspiration.",
    "Hard work pays off. Never give up on your dreams. Three months of grinding and finally seeing results!",
    "Late night coding session. The struggle is real but the rewards are worth it.",
    "Trying out a new recipe today. Wish me luck! If it works out, I'm hosting a dinner party.",
    "Fitness journey update: feeling stronger every day. Consistency is the key.",
    "Sometimes you just need to take a step back and appreciate how far you've come.",
    "The best investment you can make is in yourself. Keep learning, keep growing.",
    "Rainy days and coffee shops. Perfect combo for deep thinking.",
    "New addition to the family! Meet my new best friend.",
    "Music is the universal language of mankind. Currently obsessing over this new album.",
    "Monday motivation: Your only limit is your mind.",
    "Just had the most amazing conversation with a stranger. Humans are beautiful.",
    "Gratitude turns what we have into enough. Thankful for every moment.",
    "Dream big. Start small. Act now.",
    "The only way to do great work is to love what you do. Steve Jobs was right.",
]

comment_texts = [
    "This is amazing! Love it!",
    "So beautiful! Where is this?",
    "Goals! You're crushing it.",
    "This made my day, thank you!",
    "Absolutely stunning!",
    "Can't wait to see more!",
    "You're so talented!",
    "This is pure inspiration.",
    "Living the dream!",
    "Wow, just wow!",
    "Need to visit this place!",
    "You make it look so easy.",
    "Keep it up! You're doing great.",
    "This is everything!",
    "Obsessed with this vibe.",
    "How do you always find the best spots?",
    "Teach me your ways!",
    "The aesthetic is on point.",
    "Major inspiration right here.",
    "This deserves more likes!",
    "Your content is always top tier.",
    "I needed this motivation today.",
    "This is why I follow you.",
    "Simply gorgeous!",
    "Can we go here together next time?",
]

class Command(BaseCommand):
    help = 'Seeds the database with demo users, posts, comments, and social connections'

    def handle(self, *args, **options):
        from django.db import connection
        self.stdout.write(self.style.WARNING('Clearing existing data...'))
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA foreign_keys = OFF")
        Comment.objects.all().delete()
        LikePost.objects.all().delete()
        FollowersCount.objects.all().delete()
        Post.objects.all().delete()
        Profile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA foreign_keys = ON")

        self.stdout.write('Seeding database...')

        created_users = []
        for user_data in demo_users:
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
            )
            Profile.objects.create(
                user=user,
                id_user=user.id,
                bio=user_data['bio'],
                location=user_data['location'],
            )
            created_users.append(user)
            self.stdout.write(f'  Created user: {user_data["username"]}')

        seed_media_dir = os.path.join(settings.MEDIA_ROOT, 'post_images')
        os.makedirs(seed_media_dir, exist_ok=True)

        sample_ids = [10, 20, 25, 30, 36, 42, 48, 55, 60, 65, 68, 74, 82, 91, 96, 99, 100, 101, 102, 103, 104, 106, 110, 112, 114, 116, 118, 120, 121, 122, 123, 124, 125, 128, 130, 132, 134, 136, 138, 140]
        post_images = [f'sample_{sid}.jpg' for sid in sample_ids]

        all_posts = []
        for user in created_users:
            num_image_posts = random.randint(4, 8)
            num_text_posts = random.randint(2, 4)
            chosen_images = random.sample(post_images, min(num_image_posts, len(post_images)))

            for j, img_name in enumerate(chosen_images):
                dest_name = f"{user.username}_{j}_{img_name}"
                src = os.path.join(seed_media_dir, img_name)
                dest = os.path.join(seed_media_dir, dest_name)
                if os.path.exists(src) and not os.path.exists(dest):
                    shutil.copy2(src, dest)

                hours_ago = random.randint(1, 1680)
                created_at = timezone.now() - timedelta(hours=hours_ago)

                post = Post.objects.create(
                    user=user.username,
                    post_type='image',
                    image=f'post_images/{dest_name}',
                    caption=random.choice(image_captions),
                    created_at=created_at,
                )
                all_posts.append(post)

            for k in range(num_text_posts):
                hours_ago = random.randint(1, 1680)
                created_at = timezone.now() - timedelta(hours=hours_ago)

                post = Post.objects.create(
                    user=user.username,
                    post_type='text',
                    caption=random.choice(text_captions),
                    created_at=created_at,
                )
                all_posts.append(post)

            total = num_image_posts + num_text_posts
            self.stdout.write(f'  Created {total} posts for: {user.username}')

        self.stdout.write(f'  Total posts created: {len(all_posts)}')

        for user in created_users:
            potential_follows = [u for u in created_users if u != user]
            num_follows = random.randint(2, min(5, len(potential_follows)))
            to_follow = random.sample(potential_follows, num_follows)
            for follow_user in to_follow:
                FollowersCount.objects.create(
                    follower=user.username,
                    user=follow_user.username,
                )
        self.stdout.write(f'  Created follow relationships')

        for post in all_posts:
            num_likes = random.randint(2, min(7, len(created_users)))
            likers = random.sample(created_users, num_likes)
            for liker in likers:
                LikePost.objects.create(
                    post_id=post.id,
                    username=liker.username,
                )
            post.no_of_likes = LikePost.objects.filter(post_id=post.id).count()
            post.save()

            num_comments = random.randint(1, 5)
            commenters = random.sample(created_users, min(num_comments, len(created_users)))
            for commenter in commenters:
                hours_after = random.randint(1, 48)
                Comment.objects.create(
                    post=post,
                    user=commenter.username,
                    text=random.choice(comment_texts),
                    created_at=post.created_at + timedelta(hours=hours_after),
                )

        total_likes = LikePost.objects.count()
        total_comments = Comment.objects.count()
        total_follows = FollowersCount.objects.count()

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Seed complete!'))
        self.stdout.write(self.style.SUCCESS(f'  {len(created_users)} users'))
        self.stdout.write(self.style.SUCCESS(f'  {len(all_posts)} posts'))
        self.stdout.write(self.style.SUCCESS(f'  {total_likes} likes'))
        self.stdout.write(self.style.SUCCESS(f'  {total_comments} comments'))
        self.stdout.write(self.style.SUCCESS(f'  {total_follows} follow relationships'))
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Demo login credentials (password: test12345):'))
        for u in demo_users:
            self.stdout.write(f'  {u["username"]}')
