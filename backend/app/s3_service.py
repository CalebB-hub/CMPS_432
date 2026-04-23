import logging
from typing import Optional

import boto3
from botocore.exceptions import ClientError

from app.config import settings

logger = logging.getLogger(__name__)


class S3Service:
    """
    Service for managing file storage on AWS S3.
    Handles uploads, downloads (presigned URLs), and deletions.
    """

    def __init__(self):
        """Initialize S3 client if credentials are provided and valid."""
        # Check if credentials are configured (not placeholder values)
        aws_key = settings.aws_access_key_id or ""
        aws_secret = settings.aws_secret_access_key or ""
        bucket = settings.s3_bucket_name or ""
        
        # S3 is disabled if using placeholder values
        is_placeholder = (
            aws_key == "your_aws_access_key"
            or aws_secret == "your_aws_secret_key"
            or bucket == "your-bucket-name"
            or not (aws_key and aws_secret and bucket)
        )
        
        self.enabled = False
        self.s3_client = None
        self.bucket = None
        
        if is_placeholder:
            logger.info(
                "S3 service disabled: AWS credentials are placeholder values or incomplete. "
                "Using local storage instead. "
                "Configure AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and S3_BUCKET_NAME to enable S3."
            )
            return
        
        try:
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=aws_key,
                aws_secret_access_key=aws_secret,
                region_name=settings.aws_region or "us-east-1",
            )
            self.bucket = bucket
            
            # Test connection by checking bucket access (requires only s3:ListBucket on this bucket, not ListAllMyBuckets)
            self.s3_client.head_bucket(Bucket=bucket)
            self.enabled = True
            logger.info(f"S3 service initialized successfully with bucket: {self.bucket}")
        except Exception as e:
            logger.warning(
                f"Failed to initialize S3 client with provided credentials: {e}. "
                f"Falling back to local storage."
            )
            self.enabled = False
            self.s3_client = None
            self.bucket = None

    def upload_file(
        self, file_key: str, file_content: bytes, content_type: str = "application/octet-stream"
    ) -> bool:
        """
        Upload a file to S3.

        Args:
            file_key: Unique identifier/path in S3 (e.g., user_id/file_id/filename)
            file_content: File content as bytes
            content_type: MIME type of the file

        Returns:
            True if successful, False otherwise

        Raises:
            Exception if S3 operation fails
        """
        if not self.enabled:
            raise RuntimeError("S3 service is not enabled")

        try:
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=file_key,
                Body=file_content,
                ContentType=content_type,
            )
            logger.info(f"File uploaded to S3: {file_key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to upload file to S3 ({file_key}): {e}")
            raise

    def get_download_url(self, file_key: str, expiration: int = 3600) -> str:
        """
        Generate a presigned URL for downloading a file from S3.

        Args:
            file_key: Unique identifier/path in S3
            expiration: URL expiration time in seconds (default: 1 hour)

        Returns:
            Presigned URL for downloading the file

        Raises:
            Exception if URL generation fails
        """
        if not self.enabled:
            raise RuntimeError("S3 service is not enabled")

        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": file_key},
                ExpiresIn=expiration,
            )
            logger.info(f"Generated presigned URL for: {file_key}")
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL for {file_key}: {e}")
            raise

    def delete_file(self, file_key: str) -> bool:
        """
        Delete a file from S3.

        Args:
            file_key: Unique identifier/path in S3

        Returns:
            True if successful, False otherwise

        Raises:
            Exception if delete operation fails
        """
        if not self.enabled:
            raise RuntimeError("S3 service is not enabled")

        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=file_key)
            logger.info(f"File deleted from S3: {file_key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete file from S3 ({file_key}): {e}")
            raise


# Initialize S3 service instance
s3_service = S3Service()
