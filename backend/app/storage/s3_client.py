"""S3-compatible client for Yandex Object Storage."""

from pathlib import Path
from typing import List, Optional

import boto3
import structlog
from botocore.exceptions import ClientError

from app.core.config import settings
from app.core.exceptions import StorageException

logger = structlog.get_logger()


class S3Client:
    """Client for Yandex Object Storage (S3-compatible)."""
    
    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        bucket_name: Optional[str] = None,
        region_name: Optional[str] = None,
    ):
        self.endpoint_url = endpoint_url or settings.yandex_s3_endpoint
        self.access_key = access_key or settings.yandex_s3_access_key
        self.secret_key = secret_key or settings.yandex_s3_secret_key
        self.bucket_name = bucket_name or settings.yandex_s3_bucket
        self.region_name = region_name or settings.yandex_s3_region
        
        self.client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region_name,
        )
        
        # Ensure bucket exists
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist."""
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            try:
                self.client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": self.region_name},
                )
                logger.info("bucket_created", bucket=self.bucket_name)
            except ClientError as e:
                logger.error("bucket_creation_failed", bucket=self.bucket_name, error=str(e))
    
    def upload_file(self, local_path: str, s3_key: str) -> str:
        """Upload file to S3."""
        try:
            self.client.upload_file(local_path, self.bucket_name, s3_key)
            logger.info("file_uploaded", local_path=local_path, s3_key=s3_key)
            return f"s3://{self.bucket_name}/{s3_key}"
        
        except ClientError as e:
            logger.error("file_upload_failed", local_path=local_path, s3_key=s3_key, error=str(e))
            raise StorageException("upload_file", {"local_path": local_path, "error": str(e)})
    
    def download_file(self, s3_key: str, local_path: str) -> str:
        """Download file from S3."""
        try:
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            self.client.download_file(self.bucket_name, s3_key, local_path)
            logger.info("file_downloaded", s3_key=s3_key, local_path=local_path)
            return local_path
        
        except ClientError as e:
            logger.error("file_download_failed", s3_key=s3_key, error=str(e))
            raise StorageException("download_file", {"s3_key": s3_key, "error": str(e)})
    
    def list_objects(self, prefix: str = "") -> List[dict]:
        """List objects in bucket with optional prefix."""
        try:
            response = self.client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            objects = response.get("Contents", [])
            logger.info("objects_listed", prefix=prefix, count=len(objects))
            return objects
        
        except ClientError as e:
            logger.error("objects_list_failed", prefix=prefix, error=str(e))
            raise StorageException("list_objects", {"prefix": prefix, "error": str(e)})
    
    def generate_presigned_url(self, s3_key: str, expires_in: int = 3600) -> str:
        """Generate presigned URL for temporary access."""
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": s3_key},
                ExpiresIn=expires_in,
            )
            logger.info("presigned_url_generated", s3_key=s3_key, expires_in=expires_in)
            return url
        
        except ClientError as e:
            logger.error("presigned_url_generation_failed", s3_key=s3_key, error=str(e))
            raise StorageException(
                "generate_presigned_url", {"s3_key": s3_key, "error": str(e)}
            )
    
    def delete_object(self, s3_key: str) -> None:
        """Delete object from S3."""
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info("object_deleted", s3_key=s3_key)
        
        except ClientError as e:
            logger.error("object_delete_failed", s3_key=s3_key, error=str(e))
            raise StorageException("delete_object", {"s3_key": s3_key, "error": str(e)})