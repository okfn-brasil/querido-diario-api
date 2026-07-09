import secrets

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from config.config import load_configuration

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def validate_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Validate the API Key sent in the X-API-Key header against the keys
    configured in the QUERIDO_DIARIO_SCRAPER_API_KEYS environment variable
    (comma-separated list, allowing key rotation).

    The configuration is loaded on every request so keys can be rotated
    without restarting the application.
    """
    configured_keys = [key for key in load_configuration().scraper_api_keys if key]
    if not configured_keys:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Scraper API is not configured.",
        )
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key.",
        )
    for valid_key in configured_keys:
        if secrets.compare_digest(api_key, valid_key):
            return api_key
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid API Key.",
    )
