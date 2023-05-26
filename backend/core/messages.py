from core.limitations import Limits


USERS_HELP_USERNAME = (
    'Required to fill in.'
    f'From {Limits.MIN_LEN_USERNAME} to '
    f'{Limits.MAX_LEN_USERS_CHARFIELD} letters.'
)

USERS_HELP_FIRSTNAME = (
    'Required to fill in.'
    f'Maximum {Limits.MAX_LEN_USERS_CHARFIELD} letters.'
)

USERS_HELP_EMAIL = (
    'Required to fill in.'
    f'Maximum {Limits.MAX_LEN_EMAIL_FIELD} letters.'
)
