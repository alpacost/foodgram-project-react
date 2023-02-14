from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import AlphanumericValidator


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'
    ROLE_CHOICES = (
        (USER, 'USER'),
        (ADMIN, 'ADMIN')
    )
    role = models.CharField(
        verbose_name='Права доступа',
        max_length=10,
        choices=ROLE_CHOICES,
        default=USER
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=50,
        blank=False
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=50,
        blank=False
    )
    username = models.CharField(
        verbose_name='Логин',
        max_length=50,
        db_index=True,
        unique=True,
        validators=[AlphanumericValidator]
    )
    REQUIRED_FIELDS = ['email']

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    class Meta:
        ordering = ['id']
        constraints = [
            models.CheckConstraint(
                check=~models.Q(
                    username__iexact='me'
                ),
                name="username_is_not_me"
            )
        ]
