from typing import Any
from rest_framework.response import Response
from rest_framework import status


def api_response(
    *,
    message: str,
    data: Any = None,
    status_code: int = 200,
) -> Response:
    return Response(
        status=status_code,
        data={
            "status": status_code,
            "message": message,
            "data": data,
        },
    )
