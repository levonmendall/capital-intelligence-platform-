"""External data providers for the Capital Intelligence Platform."""
"""External data-provider adapters."""

from providers.sec_edgar import (
    SECEdgarProvider,
    SECEdgarProviderError,
)

__all__ = [
    "SECEdgarProvider",
    "SECEdgarProviderError",
]
