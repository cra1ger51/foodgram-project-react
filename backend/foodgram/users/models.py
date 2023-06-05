from django.contrib.auth.models import AbstractUser
from django.db import models

ADMIN = 'admin'


class User(AbstractUser):
    USER = 'user'
    ROLES = (
        (USER, 'User'),
        (ADMIN, 'Admin'),
    )
    role = models.CharField(
        max_length=10,
        choices=ROLES,
        default=USER)

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователь'

    def __str__(self):
        return self.username


class Subscriptions(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['author', 'user'],
                                    name='Subscribe_unique')
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
