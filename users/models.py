from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models

class User(AbstractBaseUser):
    phone = models.CharField(
        max_length=15,
        unique=True
    )
    invite_code = models.CharField(
        max_length=6,
        unique=True
    )
    activated_invite_code = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='referred_users'
    )
    USERNAME_FIELD = 'phone'

