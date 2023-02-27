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
    email = models.EmailField(
        verbose_name='Почта',
        max_length=254,
        db_index=True,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
    )
    username = models.CharField(
        verbose_name='Логин',
        max_length=150,
        db_index=True,
        unique=True,
        validators=[AlphanumericValidator]
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    class Meta:
        ordering = ['id', ]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(
                    username__iexact='me'
                ),
                name="username_is_not_me"
            )
        ]


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='Subscriber',
        verbose_name='Пользователь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Подписки',
    )

    class Meta:
        unique_together = ('user', 'author')
