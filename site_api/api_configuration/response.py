from rest_framework.response import Response


class BaseResponse(Response):
    def __init__(self, data=None, message=None, status=None):
        response_data = {
            "success": True if status // 100 == 2 else False,
            "status": status,
            "message": message,
            "data": data
        }
        super().__init__(response_data)
