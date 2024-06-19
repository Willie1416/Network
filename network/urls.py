
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new-post", views.new_post, name="new-post"),
    path("profile/<str:user_name>", views.profile_page, name="profile-page"),
    path("profile", views.follow, name="follow"),
    path("following", views.following, name="following"),

    # API routes
    path("update/<int:post_id>", views.update, name="update"),
    path("like/<int:post_id>", views.like, name="like"),

]
