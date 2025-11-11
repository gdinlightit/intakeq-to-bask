import logging
import boto3
from botocore.exceptions import ClientError
from config import settings

logger = logging.getLogger(__name__)


def upload_to_s3_and_get_url(
    file_content: bytes,
    filename: str,
) -> str:
    """Upload file to S3 and return presigned URL."""
    s3_client = boto3.client("s3", region_name=settings.AWS.REGION)

    key = f"{settings.S3.KEY_PREFIX}/{filename}"

    try:
        s3_client.put_object(
            Bucket=settings.S3.BUCKET,
            Key=key,
            Body=file_content,
            ContentType="text/csv",
        )

        url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3.BUCKET, "Key": key},
            ExpiresIn=settings.S3.SIGNED_URL_EXPIRATION,
        )

        logger.info(f"Uploaded to s3://{settings.S3.BUCKET}/{key}")
        return url

    except ClientError as e:
        logger.error(f"Failed to upload to S3: {e}")
        raise
