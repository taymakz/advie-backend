from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from site_api.api_configuration.enums import ResponseMessage


class BaseResponse(Response):
    def __init__(self, data=None, message=None, status=None):
        response_data = {
            "success": True if status // 100 == 2 else False,
            "status": status,
            "message": message,
            "data": data
        }
        super().__init__(response_data)


class PaginationApiResponse(PageNumberPagination):
    page_size_query_param = 'take'
    page_query_param = 'page'
    page_size = 20
    max_page_size = 100

    def get_paginated_response(self, data):
        current_page = self.page.number
        page_count = self.page.paginator.num_pages
        pagination = {
            'entityCount': self.page.paginator.count,
            'currentPage': self.page.number,
            'pageCount': self.page.paginator.num_pages,
            'startPage': max(current_page - 2, 1),
            'endPage': min(current_page + 2, page_count),
            'take': self.page.paginator.per_page,
            'has_next': self.page.has_next(),
            'has_previous': self.page.has_previous(),
            'data': data
        }
        response = BaseResponse(data=pagination, status=status.HTTP_200_OK,
                                message=ResponseMessage.SUCCESS.value)
        return response
