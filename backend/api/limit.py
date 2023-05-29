from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class PaginationLimit(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = settings.DEFAULT_PAGE_PAGINATION
    max_page_size = settings.MAX_PAGE_PAGINATION
