from django.urls import path
from . import views

app_name = 'auth_user'

urlpatterns = [
    path("register", views.register, name='register'),
    path("logout", views.logout_view, name='logout'),
    path("login", views.login_view, name='login'),
    path("user_profile", views.user_profile, name='user_profile'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path("new_password", views.new_password, name='new_password'),
    path("password_reset", views.password_reset_request, name="password_reset"),
    path("delete_movie_watchlist/<movie_id>", views.delete_movie_watchlist, name="delete_movie_watchlist"),
]
