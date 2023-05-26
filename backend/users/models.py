import unicodedata

from django.contrib.auth.models import AbstractUser
from django.db.models import (CASCADE, BooleanField, CharField,
                              CheckConstraint, DateTimeField, EmailField, F,
                              ForeignKey, Model, Q, UniqueConstraint)
from django.db.models.functions import Length
from django.utils.translation import gettext_lazy as _

from core.limitations import Limits
from core.messages import (USERS_HELP_EMAIL, USERS_HELP_FIRSTNAME,
                        USERS_HELP_USERNAME)
from core.validators import MinLenValidator, OneOfTwoValidator


CharField.register_lookup(Length)


class User(AbstractUser):
    email = EmailField(
        verbose_name='Email address',
        max_length=Limits.MAX_LEN_EMAIL_FIELD.value,
        unique=True,
        help_text=USERS_HELP_EMAIL,
    )
    username = CharField(
        verbose_name='username',
        max_length=Limits.MAX_LEN_USERS_CHARFIELD.value,
        unique=True,
        help_text=USERS_HELP_USERNAME,
        validators=(
            MinLenValidator(
                min_len=Limits.MIN_LEN_USERNAME,
                field='username',
            ),
            OneOfTwoValidator(field='username'),
        ),
    )
    first_name = CharField(
        verbose_name='First name',
        max_length=Limits.MAX_LEN_USERS_CHARFIELD.value,
        help_text=USERS_HELP_FIRSTNAME,
        validators=(OneOfTwoValidator(
            first_regex='[^а-яёА-ЯЁ -]+',
            second_regex='[^a-zA-Z -]+',
            field='First name'),
        ),
    )
    last_name = CharField(
        verbose_name='Last name',
        max_length=Limits.MAX_LEN_USERS_CHARFIELD.value,
        help_text=USERS_HELP_FIRSTNAME,
        validators=(OneOfTwoValidator(
            first_regex='[^а-яёА-ЯЁ -]+',
            second_regex='[^a-zA-Z -]+',
            field='Last name'),
        ),
    )
    password = CharField(
        verbose_name=_('Password'),
        max_length=128,
        help_text=USERS_HELP_FIRSTNAME,
    )
    is_active = BooleanField(
        verbose_name='Active',
        default=True,
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ('username',)
        constraints = (
            CheckConstraint(
                check=Q(username__length__gte=Limits.MIN_LEN_USERNAME.value),
                name='\nusername is too short\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.username}: {self.email}'

    @classmethod
    def normalize_email(cls, email: str) -> str:
        email = email or ""
        try:
            email_name, domain_part = email.strip().rsplit("@", 1)
        except ValueError:
            pass
        else:
            email = email_name.lower() + "@" + domain_part.lower()
        return email

    @classmethod
    def normalize_username(cls, username: str) -> str:
        return unicodedata.normalize("NFKC", username).capitalize()

    def normalize_human_names(self, name: str) -> str:
        storage = [None] * len(name)
        title = True
        idx = 0
        for letter in name:
            letter = letter.lower()
            if title:
                if not letter.isalpha():
                    continue
                else:
                    letter = letter.upper()
                    title = False
            elif letter in ' -':
                title = True
            storage[idx] = letter
            idx += 1
        return ''.join(storage[:idx])

    def clean(self) -> None:
        self.first_name = self.__normalize_human_names(self.first_name)
        self.last_name = self.__normalize_human_names(self.last_name)
        return super().clean()


class Subscriptions(Model):
    author = ForeignKey(
        verbose_name='Author of the recipe',
        related_name='subscribers',
        to=User,
        on_delete=CASCADE,
    )
    user = ForeignKey(
        verbose_name='Subscribers',
        related_name='subscriptions',
        to=User,
        on_delete=CASCADE,
    )
    date_added = DateTimeField(
        verbose_name='Date of subscribe',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Subscribe'
        verbose_name_plural = 'Subscribes'
        constraints = (
            UniqueConstraint(
                fields=('author', 'user'),
                name='\nRe-subscription\n',
            ),
            CheckConstraint(
                check=~Q(author=F('user')),
                name='\nIt is impossible to subscribe to yourself\n'
            )
        )

    def __str__(self) -> str:
        return f'{self.user.username} -> {self.author.username}'
