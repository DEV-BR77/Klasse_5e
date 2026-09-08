"""One centrally managed idle-session policy for the complete portal."""

from django.db.utils import OperationalError, ProgrammingError

from .branding import resolve_configuration
from .models import PortalConfigurationKey

SESSION_IDLE_TIMEOUT_KEY = "session_idle_timeout_minutes"
DEFAULT_IDLE_TIMEOUT_MINUTES = 15
MIN_IDLE_TIMEOUT_MINUTES = 1
MAX_IDLE_TIMEOUT_MINUTES = 120


def idle_timeout_minutes():
    try:
        configured = resolve_configuration(SESSION_IDLE_TIMEOUT_KEY)
    except (OperationalError, ProgrammingError, PortalConfigurationKey.DoesNotExist):
        return DEFAULT_IDLE_TIMEOUT_MINUTES
    if (
        isinstance(configured, bool)
        or not isinstance(configured, int)
        or not MIN_IDLE_TIMEOUT_MINUTES <= configured <= MAX_IDLE_TIMEOUT_MINUTES
    ):
        return DEFAULT_IDLE_TIMEOUT_MINUTES
    return configured
