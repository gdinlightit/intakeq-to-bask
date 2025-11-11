import logging
import asyncio
from datetime import datetime

from logger import setup_logging
from config import settings
from intakeq_client import create_intakeq_client, download_csv_export
from transformers import transform_csv
from s3_client import upload_to_s3_and_get_url

setup_logging()
logger = logging.getLogger(__name__)


async def get_data() -> bytes:
    if settings.APP.is_local:
        input_path = settings.APP.DATA_DIR / "intakeq_migration_data.csv"
        logger.info(f"[DEV] Reading local CSV from {input_path}")
        return input_path.read_bytes()

    async with create_intakeq_client() as client:
        return await download_csv_export(client)


async def transform(input_csv: bytes) -> bytes:
    bask_csv, stats = transform_csv(input_csv)

    if settings.APP.is_local:
        output_path = settings.APP.DATA_DIR / "bask_migration_data.csv"
        output_path.write_bytes(bask_csv)

    logger.info(f"Transformed {stats.successful}/{stats.total} patients successfully")
    return bask_csv


async def upload_data(input_csv: bytes) -> str:
    if settings.APP.is_local:
        return "mocked_signed_url"

    return upload_to_s3_and_get_url(
        file_content=input_csv,
        filename=f"bask_health_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    )


async def main():
    try:
        settings.APP.DATA_DIR.mkdir(parents=True, exist_ok=True)

        logger.info("Extracting data from IntakeQ")
        intakeq_csv = await get_data()
        logger.info("Done")

        logger.info("Transforming data to Bask Health format")
        bask_csv = await transform(intakeq_csv)
        logger.info("Done")

        logger.info("Uploading to S3")
        signed_url = await upload_data(bask_csv)
        logger.info("Done")

    except Exception as e:
        logger.error(f"[ERROR]: {e}", exc_info=True)
        raise

    logger.info("=" * 80)
    logger.info(f"{signed_url=}")
    logger.info("=" * 80)

    return signed_url


if __name__ == "__main__":
    asyncio.run(main())
