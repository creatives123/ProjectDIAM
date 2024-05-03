from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User

GENDER_CHOICES = (
    ("", "Please select"),
    ("M", 'Men'),
    ("F", 'Woman'),
    ("O", 'Other'),
    ("N", 'Rather not Say')
)


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    birthday = models.DateField()
    entry_date = models.DateField(auto_now_add=True)
    block_coin = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


        