"""
URL builder utilities for file storage endpoints.

This module provides functionality to build complete file URLs from relative
paths or transform legacy storage URLs to new endpoints.
"""

import os
import re


def _get_protocol_or_none(path_or_url, protocols=["http", "https", "s3"]):
    """
    Extract the protocol of the path/url if there are any.

    Accepts a list of extra protocols.

    Examples:
        >>> # Relative path with endpoint
        >>> _get_protocol_or_none('3304557/2019/file.pdf')
        "http://"

        >>> https url
        >>> _get_protocol_or_none('https://qd.nyc3.cdn.dos.com/330/file.pdf')
        "https://"

        >>> s3 url
        >>> _get_protocol_or_none('s3://data.qd.ok.org.br/3304557/file.pdf')
        "s3://"

        >>> tcp
        >>> _get_protocol_or_none('tcp://doweb.rio.rj.gov.br/portal/ed/4067')
        None

    Args:
        path_or_url: Either a relative path or a full URL
        protocols: List of protocols to be tested/checked

    Returns:
        The protocol being used from the list or None.
    """
    for protocol in protocols:
        if path_or_url.startswith(f"{protocol}://"):
            return protocol
    return None


def build_file_url(path_or_url: str) -> str:
    """
    Builds the complete file URL from a relative path or processes legacy URLs.

    This function supports three scenarios:
    1. New data: relative paths (e.g., "3304557/2019/file.txt")
    2. Old data: full URLs from old storage with automatic base URL replacement
    3. Legacy mode: full URLs returned as-is (backward compatibility)

    Environment variables:
    - QUERIDO_DIARIO_FILES_ENDPOINT: New base URL for files (can include or omit protocol)
    - REPLACE_FILE_URL_BASE: Boolean flag to enable base URL replacement (true/false)

    URL transformation rules:
    - URLs already using the correct endpoint are preserved as-is
    - Only old storage URLs are transformed:
      * querido-diario.nyc3.cdn.digitaloceanspaces.com (DigitalOcean Spaces)
      * okbr-qd-historico (S3 bucket)
    - External URLs (e.g., doweb.rio.rj.gov.br) are preserved
    - Protocol https:// is added to endpoint if not present

    Examples:
        >>> # Relative path with endpoint
        >>> os.environ['QUERIDO_DIARIO_FILES_ENDPOINT'] = 'data.qd.ok.org.br'
        >>> build_file_url('3304557/2019/file.pdf')
        'https://data.queridodiario.ok.org.br/3304557/2019/file.pdf'

        >>> # Old storage URL with replacement enabled
        >>> os.environ['REPLACE_FILE_URL_BASE'] = 'true'
        >>> build_file_url('https://qd.nyc3.cdn.dos.com/3304557/file.pdf')
        'https://data.queridodiario.ok.org.br/3304557/file.pdf'

        >>> # URL already correct - preserved
        >>> build_file_url('https://data.qd.ok.org.br/3304557/file.pdf')
        'https://data.queridodiario.ok.org.br/3304557/file.pdf'

        >>> # External URL - preserved
        >>> build_file_url('https://doweb.rio.rj.gov.br/portal/edicoes/4067')
        'https://doweb.rio.rj.gov.br/portal/edicoes/4067'

    Args:
        path_or_url: Either a relative path or a full URL

    Returns:
        Complete URL to access the file
    """
    endpoint = os.environ.get("QUERIDO_DIARIO_FILES_ENDPOINT", "")
    endpoint_protocol = _get_protocol_or_none(endpoint)
    replace_base_enabled = (
        os.environ.get("REPLACE_FILE_URL_BASE", "false").lower() == "true"
    )

    # Check if it's a URL (supports http://, https://, s3://)

    # Scenario 1: Relative path (new data)
    if _get_protocol_or_none(path_or_url) is None:
        if not endpoint:
            return path_or_url  # No endpoint configured

        # Remove protocol and trailing slash
        endpoint = endpoint.split("://", 1)[-1].rstrip("/")

        path = path_or_url.lstrip("/")

        # Check if the "relative" path actually contains the endpoint domain
        # This handles cases where DB has "data.queridodiario.ok.org.br/path"
        # without protocol
        if path.startswith(endpoint):
            # Path already contains the endpoint, just add protocol
            if endpoint_protocol is None:
                return f"https://{path}"
            else:
                return f"{endpoint_protocol}://{path}"

        # Add protocol back (default to https if original didn't have one)
        protocol_to_use = endpoint_protocol if endpoint_protocol else "https"
        return f"{protocol_to_use}://{endpoint}/{path}"

    # Scenario 2: Full URL with base replacement enabled
    if replace_base_enabled and endpoint:
        # Remove protocol and trailing slash
        endpoint = endpoint.split("://", 1)[-1].rstrip("/")

        # Check if URL already uses the correct endpoint
        # Extract domain from path_or_url and compare with endpoint (without
        # protocol)
        # Example: if endpoint is "data.queridodiario.ok.org.br"
        # and URL is "https://data.queridodiario.ok.org.br/path", preserve it
        # Remove protocol
        url_without_protocol = path_or_url.split("://", 1)[-1]

        # If URL already starts with the correct endpoint, return as-is
        if url_without_protocol.startswith(endpoint):
            return path_or_url

        # Check if URL should be transformed (old storage URLs)
        should_transform = (
            "queridodiario.nyc3.cdn.digitaloceanspaces.com" in path_or_url
            or "querido-diario.nyc3.cdn.digitaloceanspaces.com" in path_or_url
            or "okbr-qd-historico" in path_or_url
        )

        if should_transform:
            # Extract path from URL using regex
            # Pattern: <protocol>://<domain>/<path>
            # Supports: http://, https://, s3://
            pattern = r"^(https?://|s3://)[^/]+/(.+)$"
            match = re.match(pattern, path_or_url)

            if match:
                relative_path = match.group(2)
                # Add protocol back (default to https if original didn't have one)
                protocol_to_use = endpoint_protocol if endpoint_protocol else "https"
                return f"{protocol_to_use}://{endpoint}/{relative_path}"

    # Scenario 3: Legacy mode - return URL as-is
    return path_or_url
