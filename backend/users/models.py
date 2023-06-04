from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        'Email address',
        help_text='Enter email address',
        unique=True,
    )
    username = models.CharField(
        unique=True,
        max_length=30,
        verbose_name='Username'
    )
    first_name = models.CharField(
        max_length=50,
        verbose_name="First name"
    )
    last_name = models.CharField(
        max_length=50,
        verbose_name="Last name"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        ordering = ('-id',)
        verbose_name = 'User'
        verbose_name_plural = 'Users'

        constraints = (
            models.CheckConstraint(
                check=~models.Q(username__iexact='me'),
                name='username_is_not_me'
            ),
        )

    def __str__(self) -> str:
        return f'{self.username}'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Follower',
        related_name='follower',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Author',
        related_name='following',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Follow'
        verbose_name_plural = 'Follows'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='unique_follow'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('following')),
                name='user_not_equal_following'
            )
        )

    def __str__(self) -> str:
        return f'{self.user} subscribed to {self.following}'
