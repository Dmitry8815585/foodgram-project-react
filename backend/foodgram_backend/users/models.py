from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import validate_slug


class MyUser(AbstractUser):
    email = models.EmailField(unique=True, max_length=254)
    username = models.CharField(
        max_length=150, unique=True, validators=[validate_slug]
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    subscribers = models.ManyToManyField(
        "self", symmetrical=False, related_name="subscriptions"
    )

    def __str__(self):
        return self.username
