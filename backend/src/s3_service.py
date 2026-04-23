import boto3
from botocore.exceptions import ClientError
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1"),
        )
        self.bucket = os.getenv("S3_BUCKET_NAME")

    async def upload_file(self, file_key: str, file_content: bytes, content_type: str) -> bool:
        try:
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=file_key,
                Body=file_content,
                ContentType=content_type,
            )
            logger.info(f"File {file_key} uploaded to S3")
            return True
        except ClientError as e:
            logger.error(f"Failed to upload {file_key}: {e}")
            raise

    def get_download_url(self, file_key: str, expiration: int = 3600) -> str:
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": file_key},
                ExpiresIn=expiration,
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate URL for {file_key}: {e}")
            raise

    async def delete_file(self, file_key: str) -> bool:
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=file_key)
            logger.info(f"File {file_key} deleted from S3")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete {file_key}: {e}")
            raise