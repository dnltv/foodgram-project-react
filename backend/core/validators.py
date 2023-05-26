from re import compile
from string import hexdigits
from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


if TYPE_CHECKING:
    from recipes.models import Ingredient, Tag


def ingredients_validator(
    ingredients: list[dict[str, str | int]],
    ingredient: 'Ingredient',
) -> dict[int, tuple['Ingredient', int]]:
    valid_ings = {}

    for ing in ingredients:
        if not (isinstance(ing['amount'], int) or ing['amount'].isdigit()):
            raise ValidationError('Wrong amount of ingredient')

        amount = valid_ings.get(ing['id'], 0) + int(ing['amount'])
        if amount <= 0:
            raise ValidationError('Wrong amount of ingredient')

        valid_ings[ing['id']] = amount

    if not valid_ings:
        raise ValidationError('Wrong ingredients')

    db_ings = ingredient.objects.filter(pk__in=valid_ings.keys())
    if not db_ings:
        raise ValidationError('Wrong ingredients')

    for ing in db_ings:
        valid_ings[ing.pk] = (ing, valid_ings[ing.pk])

    return valid_ings


def hex_color_validator(color: str) -> str:
    color = color.strip(' #')
    if len(color) not in (3, 6):
        raise ValidationError(
            f'The color code {color} is not the correct length ({len(color)}).'
        )
    if not set(color).issubset(hexdigits):
        raise ValidationError(
            f'{color} not hexadecimal.'
        )
    if len(color) == 3:
        return f'#{color[0] * 2}{color[1] * 2}{color[2] * 2}'.upper()
    return '#' + color.upper()


def tags_exist_validator(tags_ids: list[int | str], tag: 'Tag') -> None:
    exists_tags = tag.objects.filter(id__in=tags_ids)

    if len(exists_tags) != len(tags_ids):
        raise ValidationError('A nonexistent tag is specified')


@deconstructible
class MinLenValidator:
    min_len = 0
    field = 'Transmitted value'
    message = '\n%s insufficient length.\n'

    def __init__(
        self,
        min_len: int | None = None,
        field: str | None = None,
        message: str | None = None,
    ) -> None:
        if min_len is not None:
            self.min_len = min_len
        if field is not None:
            self.field = field
        if message is not None:
            self.message = message
        else:
            self.message = self.message % field

    def __call__(self, value: int) -> None:
        if len(value) < self.min_len:
            raise ValidationError(self.message)


@deconstructible
class OneOfTwoValidator:
    first_regex = '[^а-яёА-ЯЁ]+'
    second_regex = '[^a-zA-Z]+'
    field = 'Transmitted value'
    message = '<%s> in different languages or contains more than just letters.'

    def __init__(
        self,
        first_regex: str | None = None,
        second_regex: str | None = None,
        field: str | None = None,
    ) -> None:
        if first_regex is not None:
            self.first_regex = first_regex
        if second_regex is not None:
            self.second_regex = second_regex
        if field is not None:
            self.field = field
        self.message = f'\n{self.field} {self.message}\n'

        self.first_regex = compile(self.first_regex)
        self.second_regex = compile(self.second_regex)

    def __call__(self, value: str) -> None:
        if self.first_regex.search(value) and self.second_regex.search(value):
            raise ValidationError(self.message % value)
