import hmac
from typing import Annotated

from fastapi import Header, HTTPException

from .config import settings


def require_service_token(authorization: Annotated[str | None, Header()] = None) -> None:
    if not settings.service_token:
        raise HTTPException(status_code=503, detail="service_token_not_configured")
    scheme, _, supplied = (authorization or "").partition(" ")
    valid = scheme.lower() == "bearer" and hmac.compare_digest(supplied, settings.service_token)
    if not valid:
        raise HTTPException(status_code=401, detail="authentication_required")
