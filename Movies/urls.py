from . import views
from django.urls import path

app_name = 'Movies'
urlpatterns = [
    path('search_details', views.search_details, name="search_details"),
    path('movie_details/<movie_id>', views.movie_details, name="movie_details"),
    path('watchlist_add/<movie_id>', views.watchlist_add, name="watchlist_add"),
    path('movie_rent/<movie_id>', views.movie_rent, name="movie_rent"),
    path('movie_request/<movie_id>', views.movie_request, name="movie_request"),
    path('watch_movie/<movie_id>', views.watch_movie, name="watch_movie"),
]
