**Postudio - Social Media Platform**  
   
 A Django-based social media platform with user profiles, posts, likes, and following system, rebranded as Postudio.  
**Features**  
- User authentication (signup/login/logout)  
- Image posts with captions  
- Like/unlike posts  
- Follow/unfollow users  
- User search  
- Profile pages with post grid  
- Account settings (profile pic, bio, location, password)  
- Smart feed (shows followed users' posts, fallback to global posts)  
- REST API with JWT authentication  
**Quick Start**  
python3 manage.py migrate  
 python3 manage.py seed    # Populate with 6 demo users + posts  
 python3 manage.py runserver  
   
**Demo Accounts**  
All 6 seeded users use password: test12345  
| | | |  
|-|-|-|  
| **Username** | **Bio** | **Location** |   
| john_doe | Photographer & traveler | New York, USA |   
| jane_smith | Digital artist | Coffee lover | London, UK |   
| alex_chen | Software developer by day... | San Francisco |   
| sarah_lee | Fitness enthusiast & foodie | Seoul, Korea |   
| mike_wilson | Music producer | vinyl collector | Austin, USA |   
| emma_davis | Fashion blogger & content creator | Paris, France |   
   
**REST API Endpoints**  
The project includes a full REST API using Django REST Framework with JWT authentication:  
**Authentication:**  
- POST /api/token/ - Obtain JWT token (username/password)  
- POST /api/token/refresh/ - Refresh access token  
- POST /api/register/ - Register new user  
**User:**  
- GET /api/me/ - Get current user info  
- GET /api/profile/<username>/ - Get user profile  
**Posts:**  
- GET /api/posts/ - List posts  
- POST /api/posts/ - Create new post  
- GET /api/posts/<id>/ - Get post detail  
- POST /api/posts/<id>/like/ - Like/unlike post  
- POST /api/posts/<id>/comment/ - Add comment  
**Profile Actions:**  
- GET /api/profile/<username>/ - View profile  
- POST /api/profile/<username>/follow/ - Follow/unfollow user  
**Merge Info**  
This project combines:  
- **django-social-media-template** — Frontend UI design (UIkit, Tailwind, custom CSS/JS)  
- **django-social-media-website** — Django backend + integrated templates  
