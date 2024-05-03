from __future__ import print_function
from django.shortcuts import render, redirect
from django.contrib import messages
from tmdbv3api import TMDb, Movie
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from Movies.forms import CommentForm
from Movies.models import Movies, Renting, Request, Watchlist, Comment
from Movies.utils import check_rent
from ProjectDIAM.settings import TMDB_API_KEY
from auth_user.models import Client

tmdb = TMDb()
tmdb.api_key = TMDB_API_KEY
movie = Movie()


# Create your views here.
def search_details(request):
    search = movie.search(request.POST['search_input'])

    movielist = []
    for res in search:
        if res:
            movielist.append(res)
        else:
            pass
    size = len(movielist)
    new_list = sorted(movielist, key=lambda i: i['popularity'], reverse=True)
    context = {
        'new_list': new_list,
        'size': size
    }

    return render(request, 'Movies/search_details.html', context)


def movie_details(request, movie_id):
    movie_obj = movie.details(movie_id)
    comments = None
    new_comment = None
    movie_bd = None
    movie_link = None
    comment_form = CommentForm()
    check_rent()
    
    if request.user.is_authenticated and Movies.objects.filter(tmvdbid=movie_id).count() > 0:
        if Renting.objects.filter(Q(client=Client.objects.get(user=request.user)) &
                                  Q(movies=Movies.objects.get(tmvdbid=movie_id)) &
                                  Q(rent_state="Available")).count() > 0:
            movie_link = Movies.objects.filter(tmvdbid=movie_id).values()

    if Movies.objects.filter(tmvdbid=movie_id).count() > 0:
        movie_bd = Movies.objects.get(tmvdbid=movie_id)
        comments = Comment.objects.filter(movies_id=movie_bd,active=True)

        # Comment posted
        if request.method == 'POST':
            comment_form = CommentForm(data=request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.movies = movie_bd
                new_comment.client = Client.objects.get(user=request.user)
                # Save the comment to the database
                new_comment.save()
                messages.success(request, "Your comment is awaiting moderation")
                return redirect('Movies:movie_details', movie_id)

    context = {
        'movie_obj': movie_obj,
        'movie_link': movie_link,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'movie_bd': movie_bd,
    }

    return render(request, 'Movies/movie_details.html', context)


@login_required()
def watchlist_add(request, movie_id):
    movie_obj = movie.details(movie_id)
    if request.user.is_authenticated:
        user_client = Client.objects.get(user=request.user)
        client_watchlist = Watchlist.objects.filter(client=user_client, w_movie_id=movie_id)
        if client_watchlist.count() == 0:
            Watchlist.objects.create(client=user_client, w_movie_id=movie_id, w_title=str(movie_obj['title']),
                                     w_vote_average=float(movie_obj['vote_average']),
                                     w_img=str(movie_obj['poster_path']))

            messages.success(request, "Movie added with success!")
            return redirect('Movies:movie_details', movie_id)
        else:
            messages.error(request, "You already have this movie on your watchlist")
            return redirect('Movies:movie_details', movie_id)

    context = {
        'movie_obj': movie_obj,
    }
    return render(request, 'Movies/movie_details.html', context)


@login_required()
def movie_rent(request, movie_id):
    movie_obj = movie.details(movie_id)

    if request.user.is_authenticated:
        bb_movie = Movies.objects.filter(tmvdbid=movie_id).values()

        if bb_movie.count() != 0:
            bb_client = Client.objects.filter(user=request.user).values()
            coin_left = bb_client[0]["block_coin"] - bb_movie[0]["price"]

            if coin_left >= 0:
                user_client = Client.objects.get(user=request.user)
                movie_instance = Movies.objects.get(tmvdbid=movie_id)
                Renting.objects.create(client=user_client, movies=movie_instance)
                user_client.block_coin = coin_left
                user_client.save()
                messages.success(request, "Renting successful. You have " + str(coin_left) + " Blockcoins")
                return redirect('Movies:movie_details', movie_id)
            else:
                messages.error(request, "You only have " + str(bb_client[0]["block_coin"]) + " Blockcoins, please "
                                                                                             "proceed to recharge "
                                                                                             "before trying to rent")
                return redirect('Movies:movie_details', movie_id)
        else:
            messages.error(request, "The movie you are trying to Rent isn't available. Please make a request and wait "
                                    "for your feedback")
            return redirect('Movies:movie_details', movie_id)

    else:
        messages.error(request, "Please login/register before proceeding with movie renting")

    context = {
        'movie_obj': movie_obj,
    }

    return render(request, 'Movies/movie_details.html', context)


@login_required()
def movie_request(request, movie_id):
    movie_obj = movie.details(movie_id)

    if request.user.is_authenticated:
        user_client = Client.objects.get(user=request.user)
        client_request = Request.objects.filter(client=user_client, movie_id=movie_id)
        if client_request.count() == 0:
            Request.objects.create(client=user_client, movie_id=movie_id, rq_title=str(movie_obj['title']),
                                   rq_vote_average=float(movie_obj['vote_average']),
                                   rq_img=str(movie_obj['poster_path']))
            messages.success(request, "Request Successful. You will be notified when the movie is available for "
                                      "renting")
            return redirect('Movies:movie_details', movie_id)
        else:
            messages.error(request, "You already made a request on this movie. Please wait for our response")
            return redirect('Movies:movie_details', movie_id)

    context = {
        'movie_obj': movie_obj,
    }

    return render(request, 'Movies/movie_details.html', context)


@login_required()
def watch_movie(request, movie_id):
    trailer_list = movie.videos(movie_id)

    context = {
        'movie_trailer': trailer_list[0]["key"],
    }

    return render(request, 'Movies/watch_movie.html', context)
