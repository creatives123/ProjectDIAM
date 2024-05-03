from django.shortcuts import render
from tmdbv3api import TMDb, Movie

from ProjectDIAM.settings import TMDB_API_KEY

# criar a API para ser usada nas views
tmdb = TMDb()
tmdb.api_key = TMDB_API_KEY
movie = Movie()


# Mostra o index da pagina com um conjunto de listas de filmes
def index(request):
    list_rows_index = [{"name": "Popular", "list": movie.popular()}, {"name": "Latest", "list": movie.now_playing()},
                       {"name": "Top Rated", "list": movie.top_rated()}]

    context = {
        'user': request.user,
        'lists': list_rows_index,
    }

    return render(request, 'main/index.html', context)


def navbar(request):
    context = {'user': request.user}
    return render(request, 'main/navbar.html', context)
