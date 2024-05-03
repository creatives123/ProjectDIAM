from msilib.schema import Class
from tabnanny import verbose
from django.db import models
from django.utils import timezone
from auth_user.models import Client

options_request = (("Requested", "Requested"),
                   ("Purchase Order", "Purchase Order"),
                   ("Available", "Available")
                   )

options_recharge = (("Requested", "Requested"),
                    ("Accepted", "Accepted"),
                    ("Rejected", "Rejected")
                    )

options_renting = (("Available", "Available"),
                   ("Not Available", "Not Available"),
                   )


# Create your models here.
class Movies(models.Model):
    name = models.CharField(max_length=100)
    tmvdbid = models.IntegerField(primary_key=True)
    price = models.IntegerField()
    add_date = models.DateTimeField(default=timezone.now)
    mo_img = models.CharField(max_length=500)
    mo_link = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = 'Movie Management'
        verbose_name_plural = 'Movie Management'
        ordering = ['add_date']


class Comment(models.Model):
    movies = models.ForeignKey(Movies, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    body = models.TextField()
    created_on = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.client)


class Watchlist(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    w_movie_id = models.IntegerField()
    w_title = models.CharField(max_length=100)
    w_vote_average = models.DecimalField(decimal_places=1, max_digits=3)
    w_img = models.CharField(max_length=500)
    w_add_date = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (("client", "w_movie_id"),)

    def __str__(self):
        return f"{self.client}'s WatchList"


class Renting(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    movies = models.ForeignKey(Movies, on_delete=models.CASCADE)
    re_add_date = models.DateTimeField(default=timezone.now)
    rent_state = models.CharField(default="Available", choices=options_renting, max_length=20)

    class Meta:
        ordering = ['re_add_date']

    def __str__(self):
        return f"{self.client}'s Rented Movies"


class Request(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    movie_id = models.IntegerField(blank=False)
    request_state = models.CharField(default="Requested", choices=options_request, max_length=20)
    rq_title = models.CharField(max_length=100)
    rq_vote_average = models.DecimalField(decimal_places=1, max_digits=3)
    rq_img = models.CharField(max_length=500)
    rq_add_date = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (("client", "movie_id"),)
        ordering = ['rq_add_date']
        verbose_name = 'Request Management'
        verbose_name_plural = 'Request Management'

    def __str__(self):
        return f"{self.client.user.first_name} Request Movie {self.movie_id}"


class RechargeRequest(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    coin_amount = models.IntegerField(blank=False)
    recharge_date = models.DateTimeField(default=timezone.now)
    recharge_state = models.CharField(default="Requested", choices=options_recharge, max_length=20)

    class Meta:
        ordering = ['recharge_date']
        verbose_name = 'Recharge Management'
        verbose_name_plural = 'Recharge Management'

    def __str__(self):
        return f"{self.client.user.first_name} Recharge Amount Requested: {self.coin_amount}"
