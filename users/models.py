from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None):
        if not phone:
            raise ValueError('Номер обязателен')

        user = self.model(phone=phone)
        user.set_unusable_password()
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    phone = models.CharField(
        max_length=15,
        unique=True
    )
    is_active = models.BooleanField(
        default=True
    )

    invite_code = models.CharField(
        max_length=6,
        unique=True,
        null=True,
        blank=True
    )

    activated_invite_code = models.CharField(
        max_length=6,
        null=True,
        blank=True
    )

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone
