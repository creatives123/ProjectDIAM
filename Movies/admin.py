from django.contrib import admin
from django.core.mail import send_mail
from django.db.models import Q
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from tmdbv3api import Movie, TMDb
from ProjectDIAM.settings import EMAIL_HOST_USER, TMDB_API_KEY
from auth_user.models import Client
from .models import Request, Movies, RechargeRequest, Comment, Renting

tmdb = TMDb()
tmdb.api_key = TMDB_API_KEY


# Register your models here.
@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('client', 'movie_link', 'rq_add_date', 'request_state')
    list_filter = ('request_state',)
    exclude = ("rq_title", "rq_vote_average", "rq_img",)

    def movie_link(self, request):
        link = '<a target="__blank" href="https://www.themoviedb.org/movie/%s">%s</a>' % (
            request.movie_id, request.rq_title)
        return mark_safe(link)

    def get_readonly_fields(self, request, obj=None):
        filter_edit = []
        if obj:
            filter_edit.extend(('movie_id', 'client'))
        if obj is not None and obj.request_state == 'Available':
            filter_edit.append("request_state")
        return filter_edit

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):

        if obj is not None and obj.request_state == 'Available':
            context.update({
                'show_save': False,
                'show_save_and_continue': False,
                'show_delete': False,
                'show_save_and_add_another': False
            })
        return super().render_change_form(request, context, add, change, form_url, obj)

    def save_model(self, request, obj, form, change):
        movie_obj = Movie().details(obj.movie_id)
        if obj is not None:
            obj.rq_title = movie_obj["title"]
            obj.rq_vote_average = movie_obj["vote_average"]
            obj.rq_img = movie_obj["poster_path"]

        if obj.request_state == 'Available':
            Request.objects.filter(~Q(request_state='Available'), movie_id=obj.movie_id).update(
                request_state='Available')
            send_email_costumers(movie_obj)
        super().save_model(request, obj, form, change)


@admin.register(Movies)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['name', 'movie_link', 'price', 'add_date']
    exclude = ("mo_img", "mo_link", 'name', 'add_date')

    def movie_link(self, request):
        link = '<a target="__blank" href="https://www.themoviedb.org/movie/%s">%s</a>' % (
            request.tmvdbid, request.tmvdbid)
        return mark_safe(link)

    def get_readonly_fields(self, request, obj=None):
        filter_edit = []
        if obj is not None:
            filter_edit.append("tmvdbid")
        return filter_edit

    def save_model(self, request, obj, form, change):
        if obj is not None:
            movie_obj = Movie().details(obj.tmvdbid)
            Request.objects.filter(movie_id=obj.tmvdbid).update(request_state="Available")
            obj.name = movie_obj["title"]
            obj.mo_img = movie_obj["poster_path"]
            send_email_costumers(movie_obj)
        super().save_model(request, obj, form, change)


@admin.register(RechargeRequest)
class RechargeRequestAdmin(admin.ModelAdmin):
    list_display = ('client', 'coin_amount', 'recharge_date', 'recharge_state')
    list_filter = ('recharge_state',)

    def get_readonly_fields(self, request, obj=None):
        filter_edit = []
        if obj:
            filter_edit.extend(('client', 'coin_amount', "recharge_date"))
        if obj is not None and obj.recharge_state == 'Accepted':
            filter_edit.append("recharge_state")
        return filter_edit

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if obj is not None and obj.recharge_state == 'Accepted':
            context.update({
                'show_save': False,
                'show_save_and_continue': False,
                'show_delete': False,
                'show_save_and_add_another': False
            })
        return super().render_change_form(request, context, add, change, form_url, obj)

    def save_model(self, request, obj, form, change):
        if obj.recharge_state == 'Accepted':
            client = Client.objects.get(pk=obj.client.id)
            client.block_coin = obj.client.block_coin + obj.coin_amount
            client.save()
            context = {"total": client.block_coin, "recharge": obj}
            html = get_template('email/recharge_ok.html').render(context)
            send_mail('Recharge Request', 'Your request has been fulfilled!', EMAIL_HOST_USER,

                      [client.user.email], html_message=html, fail_silently=True)
            super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('client', 'body', 'movies', 'created_on', 'active')
    list_filter = ('active', 'created_on')
    search_fields = ('client', 'body')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)


def send_email_costumers(movie):

    for data in Request.objects.filter(movie_id=movie.id).values('client__user__email', 'id'):
        request_obj = Request.objects.get(pk=data['id'])
        context = {"user": request_obj.client.user, 'movie': movie}
        html = get_template('email/movie_available.html').render(context)
        send_mail('New Movie Added', 'Your request has been fulfilled!', EMAIL_HOST_USER,
                  [data['client__user__email']], html_message=html, fail_silently=True)


@admin.register(Renting)
class RentingAdmin(admin.ModelAdmin):
    list_display = ['client', 'movies', 're_add_date', 'rent_state']
    search_fields = ('client', 'rent_state')

    def get_readonly_fields(self, request, obj=None):
        filter_edit = ['client', 'movies']
        return filter_edit
