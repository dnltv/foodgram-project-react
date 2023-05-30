from django.contrib.admin import ModelAdmin, register

from .models import Follow, User


@register(User)
class UserAdmin(ModelAdmin):
    search_fields = ('email', 'username')
    list_display = ('email', 'first_name', 'last_name')
    list_filter = ('email', 'username')
    empty_value_display = '-empty-'


@register(Follow)
class FollowAdmin(ModelAdmin):
    search_fields = ('user', 'following')
    list_display = ('pk', 'user', 'following')
    list_filter = ('user', 'following')
    empty_value_display = '-empty-'
