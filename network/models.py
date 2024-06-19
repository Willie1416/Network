from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Post by {self.user.username}'
    
    def total_likes(self):
        return self.likes.count()

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    is_like = models.BooleanField(default=True)

    def __str__(self):
        return f'Like by {self.user.username} on {self.post.user} Post'

class Follower(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    user_follows = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_follows")

    def __str__(self):
        return f'{self.user.username} follows {self.user_follows.username}'


