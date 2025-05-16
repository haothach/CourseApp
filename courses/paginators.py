from rest_framework.pagination import PageNumberPagination


class CoursePaginator(PageNumberPagination):
    page_size = 2

class CategoryPaginator(PageNumberPagination):
    page_size = 20