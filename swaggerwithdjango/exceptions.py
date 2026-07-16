from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError, AuthenticationFailed, NotAuthenticated
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from swaggerwithdjango.bugsnag import notify_bugsnag
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        request = context.get("request")
        view = context.get("view")

        if isinstance(exc, (ValidationError, AuthenticationFailed, NotAuthenticated, TokenError, InvalidToken)):
            pass
        elif isinstance(exc, (ObjectDoesNotExist, PermissionDenied)):
            notify_bugsnag(
                exc,
                severity="warning",
                context=f"{view.__class__.__name__}.{request.method}" if view else None,
                metadata={
                    "request": {
                        "path": request.path,
                        "method": request.method,
                        "query_params": dict(request.GET),
                    }
                },
                user={
                    "id": request.user.id if request.user.is_authenticated else None,
                    "username": request.user.username if request.user.is_authenticated else None,
                } if hasattr(request, "user") else None,
            )
        else:
            notify_bugsnag(
                exc,
                severity="error",
                context=f"{view.__class__.__name__}.{request.method}" if view else None,
                metadata={
                    "request": {
                        "path": request.path,
                        "method": request.method,
                        "query_params": dict(request.GET),
                        "data": request.data if hasattr(request, "data") else None,
                    }
                },
                user={
                    "id": request.user.id if request.user.is_authenticated else None,
                    "email": request.user.email if request.user.is_authenticated else None,
                    "username": request.user.username if request.user.is_authenticated else None,
                } if hasattr(request, "user") else None,
            )
            logger.exception("Unhandled exception in view")

    return response
