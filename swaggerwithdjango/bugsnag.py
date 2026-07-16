import bugsnag
from django.conf import settings


def configure_bugsnag():
    if not settings.BUGSNAG.get("api_key"):
        return

    bugsnag.configure(
        api_key=settings.BUGSNAG["api_key"],
        project_root=settings.BUGSNAG["project_root"],
        release_stage=settings.BUGSNAG["release_stage"],
        notify_release_stages=settings.BUGSNAG["notify_release_stages"],
        app_version=settings.BUGSNAG.get("app_version"),
        auto_capture_sessions=settings.BUGSNAG.get("auto_capture_sessions", True),
        params_filters=settings.BUGSNAG.get("params_filters", []),
    )


def notify_bugsnag(exception, severity="error", context=None, metadata=None, user=None):
    if not settings.BUGSNAG.get("api_key"):
        return

    bugsnag.notify(
        exception,
        severity=severity,
        context=context,
        metadata=metadata or {},
        user=user,
    )


def leave_breadcrumb(message, metadata=None, breadcrumb_type="manual"):
    if not settings.BUGSNAG.get("api_key"):
        return

    bugsnag.leave_breadcrumb(
        message,
        metadata=metadata or {},
        type=breadcrumb_type,
    )
