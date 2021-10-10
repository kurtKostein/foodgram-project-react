from rest_framework import pagination


class BasePagination(pagination.PageNumberPagination):
    page_size_query_param = 'limit'
