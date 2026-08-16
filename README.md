# Postudio - Social Media Platform

**Postudio** is a modern, Django-based social media platform designed for sharing and discovering images. Built with a focus on simplicity and performance, it enables users to connect through visual content while providing robust social features.

## 📸 Overview

Postudio transforms the social media experience into a picture-focused platform where users can express themselves through images, captions, and meaningful interactions. The platform combines a clean, responsive frontend with a powerful Django backend, delivering a seamless experience across devices.

## ✨ Features

### Core Functionality
- **User Authentication**: Secure signup, login, and logout systems
- **Image Posts**: Share images with expressive captions
- **Social Interactions**: Like/unlike posts and follow/unfollow other users
- **Smart Feed**: Curated content from followed users with fallback to global posts
- **User Search**: Discover and connect with other users

### Profile Experience
- **Personal Profiles**: Display profile pictures, bios, and locations
- **Post Grid**: Visual gallery of user's posts
- **Account Settings**: Update profile picture, biography, and location
- **Password Management**: Secure password change functionality

### REST API
A complete REST API using Django REST Framework with JWT authentication enables programmatic access:

#### Authentication Endpoints
- `POST /api/token/` - Obtain JWT token via username/password
- `POST /api/token/refresh/` - Refresh access tokens
- `POST /api/register/` - Register new accounts

#### User & Profile
- `GET /api/me/` - Retrieve current user information
- `GET /api/profile/<username>/` - View user profile details
- `POST /api/profile/<username>/follow/` - Follow/unfollow functionality

#### Posts
- `GET /api/posts/` - List posts (followed users + global fallback)
- `POST /api/posts/` - Create new image posts
- `GET /api/posts/<id>/` - Get detailed post information
- `POST /api/posts/<id>/like/` - Like/unlike posts
- `POST /api/posts/<id>/comment/` - Add comments to posts

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

```bash
# Clone the repository
git clone https://github.com/omarwael78/Postudio-Platform.git

# Navigate to project directory
cd Postudio-Platform

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python3 manage.py migrate

# Seed with demo data (includes 6 demo users with posts)
python3 manage.py seed

# Start development server
python3 manage.py runserver
```

### Demo Accounts
All seeded accounts use the password: `test12345`

| Username | Bio | Location |
|----------|-----|----------|
| john_doe | Photographer & traveler | New York, USA |
| jane_smith | Digital artist | London, UK |
| alex_chen | Software developer by day... | San Francisco |
| sarah_lee | Fitness enthusiast & foodie | Seoul, Korea |
| mike_wilson | Music producer | vinyl collector | Austin, USA |
| emma_davis | Fashion blogger & content creator | Paris, France |

## 🛠 Technology Stack

### Backend
- **Django 3.2+** - Python web framework
- **Django REST Framework** - API construction
- **JWT Authentication** - Secure token-based auth
- **SQLite** - Development database (PostgreSQL production-ready)

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Custom styles with TailwindCSS
- **JavaScript (Vanilla)** - Interactive features
- **Uikit** - UI component library
- **Font Awesome** - Icon set

## 📁 Project Structure

```
Postudio-Platform/
├── manage.py          # Django entry point
├── db.sqlite3        # Development database
├── requirements.txt  # Python dependencies
├── README.md         # Project documentation
├──.git/             # Git version control
├── media/           # User-uploaded media files
├── static/          # Static assets (CSS, JS, images)
├── templates/       # HTML templates
└── postudio/        # Django application
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py     # Database models
    ├── views.py      # View logic
    ├── serializers.py # API serializers
    ├── urls.py       # URL routing
    └── migrations/   # Database migrations
```

## 🎯 Use Cases

- **Personal branding**: Share your photography or artwork
- **Community building**: Connect with like-minded individuals
- **Content discovery**: Explore posts from followed users
- **Social networking**: Follow friends and discover new interests
- **API integration**: Build mobile apps or third-party integrations

## 📦 Deployment

### Production Considerations
- Use PostgreSQL instead of SQLite for production
- Set `DEBUG = False` in `settings.py`
- Configure `ALLOWED_HOSTS` securely
- Use environment variables for `SECRET_KEY`
- Consider adding `requirements.txt` and `Procfile` for Heroku/Cloud deployment
- Enable HTTPS for production domains

## 👥 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.

---

**Postudio** - Where moments become memories, and connections are made through images.