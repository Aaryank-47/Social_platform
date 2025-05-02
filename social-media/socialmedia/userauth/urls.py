from django.contrib import admin
from django.urls import path
from django.conf import settings
from userauth import views
from django.conf.urls.static import static
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from userauth.models import LikePost

urlpatterns = [
    path('',views.home),
    path('loginn/',views.loginn),
    path('signup/',views.signup),
    path('logoutt/',views.logoutt),
    path('upload',views.upload),
    path('likes/<uuid:id>', views.likes, name='likes'),
    path('like-post/<uuid:id>', views.likes, name='like-post'),
    # path('#<str:id>', views.home_post),
    path('uuid:id>/', views.home_post, name='post_detail'), # Assuming your Post ID is a UUID
    # path('explore',views.explore),
    path('profile/<str:id_user>', views.profile, name='profile'),
    path('delete/<str:id>', views.delete),
    path('search-results/', views.search_results, name='search_results'),
    path('connect', views.connect, name='connect'),
    path('recommendations/', views.get_user_recommendations, name='recommendations'),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
]

urlpatterns = urlpatterns+static(settings.MEDIA_URL,
document_root=settings.MEDIA_ROOT)
    
@login_required(login_url='/loginn')
def home(request):
    user = request.user
    user_connections = User.objects.filter(
        Q(received_requests__sender=user, received_requests__is_accepted=True) |
        Q(sent_requests__receiver=user, sent_requests__is_accepted=True)
    ).exclude(id=user.id)

    liked_posts = LikePost.objects.filter(username=request.user.username).values_list('post_id', flat=True)

    context = {
        'user_connections': user_connections,
        'liked_posts': liked_posts,
    }
    return render(request, 'main.html', context)
    
