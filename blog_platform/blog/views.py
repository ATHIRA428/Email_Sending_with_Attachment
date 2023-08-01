from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import BlogPost, Comment
from .serializers import UserSerializer, BlogPostSerializer, CommentSerializer, AdminUserRegistrationSerializer
from django.contrib.auth import get_user_model
from .permissions import IsOwnerOrReadOnly
from rest_framework.generics import CreateAPIView

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        ctx = {'user': user.username}
        subject = "Welcome to Blogging Platform"
        email_template = 'user_registration_mail.html'  
        email_content = render_to_string(email_template, ctx)
        from_email = 'your_email@example.com'
        to_email = user.email
        send_mail(subject, '', from_email, [to_email], html_message=email_content)

        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)

class UserLoginView(generics.CreateAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response({'refresh': str(refresh), 'access': str(refresh.access_token)}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class BlogPostListCreateView(CreateAPIView):
    serializer_class = BlogPostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        created_post = serializer.instance

        subject = "Post Created"
        from_email = "athirasaseendran428@gmail.com"
        recipient_list = [created_post.user.email] 

        html_file_path = "templates/blog_post_notification.html"
        with open(html_file_path, "r") as html_file:
            html_content = html_file.read()
        html_content = html_content.replace("{{ BlogPost.title }}", created_post.title)
        html_content = html_content.replace("{{ BlogPost.content }}", created_post.content)
        if created_post.file:
            html_content = html_content.replace("{{ BlogPost.file.path }}", created_post.file.path)
        else:
            html_content = html_content.replace("{{ BlogPost.file }}", "")

        email = EmailMultiAlternatives(subject, "", from_email, recipient_list)
        email.attach_alternative(html_content, "text/html")
        if created_post.file:
            email.attach_file(created_post.file.path)

        email.send()

        return Response({"message": "Post created Successfully"}, status=status.HTTP_201_CREATED)



class BlogPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [IsOwnerOrReadOnly]
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        blog_post = self.get_object()
        comments = Comment.objects.filter(blog_post=blog_post)
        comment_serializer = CommentSerializer(comments, many=True)
        response.data['comments'] = comment_serializer.data

        return response


class CommentListCreateView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to update this comment.")
        serializer.save()
    
    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this comment.")
        instance.delete()

class AdminUserRegistrationView(generics.CreateAPIView):
    serializer_class = AdminUserRegistrationSerializer
    permission_classes = [IsAdminUser] 

    def perform_create(self, serializer):
        serializer.save()


