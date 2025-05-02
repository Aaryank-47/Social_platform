from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime

User = get_user_model()

# Create your models here.
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField(primary_key=True, default=0)
    bio = models.TextField(blank=True, default='')
    profileimg = models.ImageField(upload_to='profile_images', default='blank-profile-picture.png')
    location = models.CharField(max_length=100, blank=True, default='')
    phone = models.CharField(max_length=15, blank=True, default='')
    

    def __str__(self):
        return self.user.username

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.CharField(max_length=100)
    image = models.ImageField(upload_to='post_images')
    caption = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)
    no_of_likes = models.IntegerField(default=0)
    allowed_viewers = models.ManyToManyField(User, blank=True, related_name='allowed_posts')  # Users allowed to view this post

    def __str__(self):
        return self.user

class LikePost(models.Model):
    post_id = models.CharField(max_length=36)  # UUID as string
    username = models.CharField(max_length=150)
    #created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post_id', 'username')  # Prevent duplicate likes

# class Followers(models.Model):
#     follower = models.CharField(max_length=100)
#     user = models.CharField(max_length=100)

#     def __str__(self):
#         return self.user
class ConnectionRequest(models.Model):
    sender = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'receiver')  # Taaki ek hi request bar-bar na bhej paye

    def __str__(self):
        status = 'Accepted' if self.is_accepted else 'Pending'
        return f"{self.sender.username} -> {self.receiver.username} ({status})"

