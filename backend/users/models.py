from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Model representing a Custom user.
    """
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'

    ROLES = [
        (ADMIN, 'administrator'),
        (MODERATOR, 'moderator'),
        (USER, 'user')
    ]
    username = models.CharField(
        help_text='Enter username',
        max_length=150,
        unique=True
    )
    email = models.EmailField(
        help_text='Enter e-mail',
        max_length=254,
        unique=True
    )
    first_name = models.CharField(
        help_text='Enter first name',
        max_length=150,
        blank=True,
        null=True
    )
    last_name = models.CharField(
        help_text='Enter last name',
        max_length=150,
        blank=True,
        null=True
    )
    bio = models.TextField(
        'About me',
        help_text='Enter something about yourself',
        blank=True,
        null=True
    )
    role = models.CharField(
        max_length=20,
        choices=ROLES,
        default=USER
    )
    confirmation_code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Authorization code'
    )

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    class Meta:
        ordering = ('id',)
        verbose_name = 'User'
        verbose_name_plural = 'Users'

        constraints = [
            models.CheckConstraint(
                check=~models.Q(username__iexact='me'),
                name='username_is_not_me'
            )
        ]

    def __str__(self):
        return self.username
