import time
import logging
import json
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):


    def process_request(self, request):
        request._start_time = time.time()
        
        logger.info(
            f"[REQUEST] {request.method} {request.path}",
            extra={
                "method": request.method,
                "path": request.path,
                "query_params": dict(request.GET),
                "ip_address": self.get_client_ip(request),
                "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                "user": str(request.user) if hasattr(request, "user") else "Anonymous",
            }
        )

    def process_response(self, request, response):
        """Called after the view - log response with duration"""
        if hasattr(request, "_start_time"):
            duration = time.time() - request._start_time
            duration_ms = round(duration * 1000, 2)
            
            if response.status_code >= 500:
                log_level = logging.ERROR
            elif response.status_code >= 400:
                log_level = logging.WARNING
            else:
                log_level = logging.INFO
            
            logger.log(
                log_level,
                f"[RESPONSE] {request.method} {request.path} - {response.status_code} ({duration_ms}ms)",
                extra={
                    "method": request.method,
                    "path": request.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "ip_address": self.get_client_ip(request),
                    "user": str(request.user) if hasattr(request, "user") else "Anonymous",
                }
            )
        
        return response

    def process_exception(self, request, exception):
        """Called when a view raises an exception"""
        logger.exception(
            f"[EXCEPTION] {request.method} {request.path} - {exception.__class__.__name__}: {str(exception)}",
            extra={
                "method": request.method,
                "path": request.path,
                "exception_type": exception.__class__.__name__,
                "ip_address": self.get_client_ip(request),
                "user": str(request.user) if hasattr(request, "user") else "Anonymous",
            }
        )

    @staticmethod
    def get_client_ip(request):
        """Extract real client IP even behind proxy/load balancer"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "")
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Adds security headers to all responses.
    Production best practice for API security.
    """

    def process_response(self, request, response):
        response["X-Content-Type-Options"] = "nosniff"
        
        response["X-XSS-Protection"] = "1; mode=block"
        
        if request.path.startswith("/api/"):
            response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response["Pragma"] = "no-cache"
        
        return response


class CorrelationIdMiddleware(MiddlewareMixin):


    def process_request(self, request):
        import uuid
        correlation_id = request.META.get("HTTP_X_REQUEST_ID") or str(uuid.uuid4())
        request.correlation_id = correlation_id

    def process_response(self, request, response):
        if hasattr(request, "correlation_id"):
            response["X-Request-ID"] = request.correlation_id
        return response
