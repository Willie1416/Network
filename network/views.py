from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

from .models import User, Post, Follower, Like


def index(request):
    # Get all the post with latest first
    posts = Post.objects.all().order_by("-timestamp")

    # Limit to only 10 posts per page
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html",{
        "page_obj" : page_obj,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def new_post(request):

    if request.method == "POST":

        # Get the content from the POST request
        content = request.POST["new-post"]
        
        # Create a new post object
        new_post = Post(
            user=request.user,
            content=content
        )

        new_post.save()

        return HttpResponseRedirect(reverse("index"))
    return render(request, "network/index.html")


# Function to go to the profile page clicked on
def profile_page(request, user_name):
    
    # Load the user object and its posts
    user = User.objects.get(username=user_name)
    posts = Post.objects.filter(user=user).order_by("-timestamp")

    # Returns all the user the profile page is following
    following = Follower.objects.filter(user=user)

    # Returns all the followers of the profile page
    followers = Follower.objects.filter(user_follows=user)
    
    # Check if you're on your own profile page
    is_user = (user != request.user)
            
    # Check if the user visiting is following the profile page user
    follows = False
    if request.user.is_authenticated:
        follows = Follower.objects.filter(user=request.user, user_follows=user).exists()

    # Paginator
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'network/profile.html', {
        'user': user,
        'page_obj': page_obj,
        'is_user': is_user,
        'followers': followers,
        'following': following,
        'follows': follows
        })


# Function to start follow someone or unfollow
@login_required(login_url='login')
def follow(request):

    if request.method == "POST":

        # Get the value if they are following or unfollowing
        value = request.POST.get('action')
        user = request.user
        user_visiting = User.objects.get(username=request.POST.get('user-visiting'))

        if (value == "follow"):
            Follower.objects.create(user=user, user_follows=user_visiting)
        else:
            Follower.objects.filter(user=user, user_follows=user_visiting).delete()

        return HttpResponseRedirect(reverse('profile-page', args=[user_visiting.username]))  

    return render(request, "network/profile.html")


# Function to return the posts of the people the user follows
def following(request):
    
    # Returns a list of all the profiles the user is following
    following_users = Follower.objects.filter(user=request.user).values_list('user_follows', flat=True)
    posts = Post.objects.filter(user__in=following_users).order_by("-timestamp")

    # Paginator
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/following.html",{
        'page_obj': page_obj
    })


@csrf_exempt
def update(request, post_id):

    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)

    # Query for requested post
    try:
        post = Post.objects.get(user=request.user, pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Get the data from the body
    data = json.loads(request.body)

    # Get content for the updated content
    content = data.get('content')

    # Update the content in the post
    post.content = content
    post.timestamp = datetime.now()
    post.save()
    return JsonResponse({"message": "Post updated successfully.",
                         "timestamp": post.timestamp.strftime("%B %d, %Y, %I:%M %p")}, status=200)


@csrf_exempt
def like(request, post_id):

    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)

    # Query for requested post
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Create a new like for the post if not liked or else get the like the user have already on the post
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    # If post already liked and button pressed then unlike
    if not created:
        like.delete()
        liked = False
    # If post is not already liked then like the post
    else:
        liked = True

    like_count = post.total_likes()


    post.save()
    return JsonResponse({"like_count": like_count, "liked": liked})
