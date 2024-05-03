from datetime import timedelta
from django.db.models import Q
from django.utils import timezone
from Movies.models import Renting
from ProjectDIAM.settings import RENT_LIMIT_DAYS


def check_rent():
    Renting.objects.filter(~Q(rent_state="Not Available"), re_add_date__lte=timezone.now()-timedelta(
        days=RENT_LIMIT_DAYS)).update(rent_state="Not Available")


