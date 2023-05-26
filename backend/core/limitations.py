from enum import Enum, IntEnum


class UrlQueries(str, Enum):
    SEARCH_ING_NAME = 'name'
    SHOP_CART = 'is_in_shopping_cart'
    FAVORITE = 'is_favorited'
    TAGS = 'tags'
    AUTHOR = 'author'


class Limits(IntEnum):
    MAX_LEN_EMAIL_FIELD = 256
    MAX_LEN_USERS_CHARFIELD = 32
    MIN_LEN_USERNAME = 3
    MAX_LEN_RECIPES_TEXTFIELD = 5000
    MAX_LEN_RECIPES_CHARFIELD = 64
    MAX_LEN_MEASUREMENT = 256
    MAX_AMOUNT_INGREDIENTS = 32
    MIN_AMOUNT_INGREDIENTS = 1
    MAX_COOKING_TIME = 300
    MIN_COOKING_TIME = 1


class Tuples(tuple, Enum):
    RECIPE_IMAGE_SIZE = 500, 300
    SYMBOL_TRUE_SEARCH = '1', 'true'
    SYMBOL_FALSE_SEARCH = '0', 'false'
    ADD_METHODS = 'GET', 'POST'
    DEL_METHODS = 'DELETE',
    ACTION_METHODS = 'GET', 'POST', 'DELETE'
    UPDATE_METHODS = 'PUT', 'PATCH'

