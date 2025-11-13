import httpx
import logging
from config import settings

logger = logging.getLogger(__name__)


def create_intakeq_client() -> httpx.AsyncClient:
    """Create configured httpx client for IntakeQ API."""
    return httpx.AsyncClient(
        base_url=settings.INTAKEQ.BASE_URL,
        headers={
            "X-Auth-Key": settings.INTAKEQ.API_KEY.get_secret_value(),
            "Content-Type": "application/json",
        },
        timeout=30.0,
    )


async def download_csv_export(client: httpx.AsyncClient) -> bytes:
    """Download CSV export from IntakeQ API using configured export profile."""
    # TODO: Verify exact endpoint from IntakeQ API docs
    response = await client.get(
        f"/export/{settings.INTAKEQ.EXPORT_PROFILE_ID}", params={"format": "csv"}
    )
    response.raise_for_status()

    logger.info(f"Downloaded CSV export: {len(response.content)} bytes")
    return response.content
