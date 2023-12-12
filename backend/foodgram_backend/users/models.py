from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class MyUser(AbstractUser):
    email = models.EmailField(unique=True, max_length=254)
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_ (
            "Letters, digits, and @/./+/-/_ only."
        ),
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message=_(
                    "Enter a valid username."
                ),
                code='invalid_username',
            ),
        ],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    subscriptions = models.ManyToManyField(
        'self', through='UserSubscription',
        symmetrical=False, related_name='subscribers'
    )

    def __str__(self):
        return self.username


class UserSubscription(models.Model):

    from_user = models.ForeignKey(
        'MyUser', related_name='subscriptions_from', on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        'MyUser', related_name='subscriptions_to', on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['from_user', 'to_user']

    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username}"
