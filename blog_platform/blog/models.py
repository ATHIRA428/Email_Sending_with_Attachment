from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
import base64

class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

class BlogPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    file = models.FileField(upload_to='blog_post_files/', null=True, blank=True)

    def __str__(self):
        return self.title




class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.blog_post}"
