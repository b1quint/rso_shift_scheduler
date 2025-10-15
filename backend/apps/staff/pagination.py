from rest_framework.pagination import PageNumberPagination


class LargeResultsSetPagination(PageNumberPagination):
    """
    Pagination class that allows clients to request large page sizes.
    Useful for availability data where we need all records in a date range.
    """
    page_size = 20
    page_size_query_param = 'page_size'  # Allow client to override page size
    max_page_size = 10000  # Maximum allowed page size
