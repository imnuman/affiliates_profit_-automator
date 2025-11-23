"""AWS S3 storage service for file uploads and management."""
from typing import Optional, Dict, Any, List, BinaryIO
from datetime import datetime, timedelta
import os
import mimetypes
from pathlib import Path
import aioboto3
from botocore.exceptions import ClientError

from app.core.logging import logger
from app.core.exceptions import ServiceException
from app.config import settings


class S3StorageService:
    """Service for managing file uploads and downloads with AWS S3."""

    def __init__(
        self,
        bucket_name: Optional[str] = None,
        region: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
    ):
        """
        Initialize S3 storage service.

        Args:
            bucket_name: S3 bucket name
            region: AWS region
            access_key: AWS access key ID
            secret_key: AWS secret access key
        """
        self.bucket_name = bucket_name or os.getenv("AWS_S3_BUCKET_NAME")
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.access_key = access_key or os.getenv("AWS_ACCESS_KEY_ID")
        self.secret_key = secret_key or os.getenv("AWS_SECRET_ACCESS_KEY")

        if not self.bucket_name:
            raise ServiceException("S3 bucket name not configured")

        self.session = aioboto3.Session(
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
        )

    async def upload_file(
        self,
        file_data: bytes,
        file_name: str,
        folder: str = "uploads",
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        public: bool = False,
    ) -> Dict[str, str]:
        """
        Upload a file to S3.

        Args:
            file_data: File content as bytes
            file_name: Name of the file
            folder: Folder/prefix in S3 bucket
            content_type: MIME type of the file
            metadata: Additional metadata to store with the file
            public: Whether to make the file publicly accessible

        Returns:
            Dictionary with file_url, file_key, and bucket_name
        """
        try:
            # Generate S3 key
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            safe_filename = self._sanitize_filename(file_name)
            s3_key = f"{folder}/{timestamp}_{safe_filename}"

            # Detect content type if not provided
            if not content_type:
                content_type, _ = mimetypes.guess_type(file_name)
                if not content_type:
                    content_type = "application/octet-stream"

            # Prepare upload arguments
            upload_args = {
                "ContentType": content_type,
            }

            if metadata:
                upload_args["Metadata"] = metadata

            if public:
                upload_args["ACL"] = "public-read"

            # Upload to S3
            async with self.session.client("s3") as s3:
                await s3.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=file_data,
                    **upload_args,
                )

            # Generate URL
            if public:
                file_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            else:
                # Generate presigned URL for private files (valid for 1 hour)
                file_url = await self.generate_presigned_url(s3_key, expires_in=3600)

            logger.info(f"File uploaded to S3: {s3_key}")

            return {
                "file_url": file_url,
                "file_key": s3_key,
                "bucket_name": self.bucket_name,
            }

        except ClientError as e:
            logger.error(f"S3 upload error: {str(e)}")
            raise ServiceException(f"Failed to upload file to S3: {str(e)}")
        except Exception as e:
            logger.error(f"File upload error: {str(e)}")
            raise ServiceException(f"File upload failed: {str(e)}")

    async def download_file(self, file_key: str) -> bytes:
        """
        Download a file from S3.

        Args:
            file_key: S3 object key

        Returns:
            File content as bytes
        """
        try:
            async with self.session.client("s3") as s3:
                response = await s3.get_object(Bucket=self.bucket_name, Key=file_key)

                # Read the streaming body
                async with response["Body"] as stream:
                    file_data = await stream.read()

            logger.info(f"File downloaded from S3: {file_key}")
            return file_data

        except ClientError as e:
            logger.error(f"S3 download error: {str(e)}")
            raise ServiceException(f"Failed to download file from S3: {str(e)}")
        except Exception as e:
            logger.error(f"File download error: {str(e)}")
            raise ServiceException(f"File download failed: {str(e)}")

    async def delete_file(self, file_key: str) -> bool:
        """
        Delete a file from S3.

        Args:
            file_key: S3 object key

        Returns:
            True if successful
        """
        try:
            async with self.session.client("s3") as s3:
                await s3.delete_object(Bucket=self.bucket_name, Key=file_key)

            logger.info(f"File deleted from S3: {file_key}")
            return True

        except ClientError as e:
            logger.error(f"S3 delete error: {str(e)}")
            raise ServiceException(f"Failed to delete file from S3: {str(e)}")
        except Exception as e:
            logger.error(f"File delete error: {str(e)}")
            raise ServiceException(f"File delete failed: {str(e)}")

    async def delete_files(self, file_keys: List[str]) -> Dict[str, bool]:
        """
        Delete multiple files from S3.

        Args:
            file_keys: List of S3 object keys

        Returns:
            Dictionary mapping file_key to success status
        """
        try:
            async with self.session.client("s3") as s3:
                # Prepare delete objects
                objects = [{"Key": key} for key in file_keys]

                response = await s3.delete_objects(
                    Bucket=self.bucket_name, Delete={"Objects": objects}
                )

                # Track results
                results = {key: False for key in file_keys}

                if "Deleted" in response:
                    for obj in response["Deleted"]:
                        results[obj["Key"]] = True

                logger.info(f"Deleted {len(response.get('Deleted', []))} files from S3")
                return results

        except Exception as e:
            logger.error(f"Bulk delete error: {str(e)}")
            raise ServiceException(f"Bulk delete failed: {str(e)}")

    async def file_exists(self, file_key: str) -> bool:
        """
        Check if a file exists in S3.

        Args:
            file_key: S3 object key

        Returns:
            True if file exists
        """
        try:
            async with self.session.client("s3") as s3:
                await s3.head_object(Bucket=self.bucket_name, Key=file_key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise

    async def get_file_metadata(self, file_key: str) -> Dict[str, Any]:
        """
        Get metadata for a file in S3.

        Args:
            file_key: S3 object key

        Returns:
            Dictionary with file metadata
        """
        try:
            async with self.session.client("s3") as s3:
                response = await s3.head_object(Bucket=self.bucket_name, Key=file_key)

            return {
                "content_type": response.get("ContentType"),
                "content_length": response.get("ContentLength"),
                "last_modified": response.get("LastModified"),
                "metadata": response.get("Metadata", {}),
                "etag": response.get("ETag"),
            }

        except ClientError as e:
            logger.error(f"Failed to get file metadata: {str(e)}")
            raise ServiceException(f"Failed to get file metadata: {str(e)}")

    async def list_files(
        self, prefix: str = "", max_keys: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        List files in S3 bucket.

        Args:
            prefix: Prefix to filter files
            max_keys: Maximum number of files to return

        Returns:
            List of file information dictionaries
        """
        try:
            async with self.session.client("s3") as s3:
                response = await s3.list_objects_v2(
                    Bucket=self.bucket_name, Prefix=prefix, MaxKeys=max_keys
                )

            files = []
            for obj in response.get("Contents", []):
                files.append(
                    {
                        "key": obj["Key"],
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"],
                        "etag": obj["ETag"],
                    }
                )

            return files

        except ClientError as e:
            logger.error(f"Failed to list files: {str(e)}")
            raise ServiceException(f"Failed to list files: {str(e)}")

    async def generate_presigned_url(
        self, file_key: str, expires_in: int = 3600
    ) -> str:
        """
        Generate a presigned URL for temporary file access.

        Args:
            file_key: S3 object key
            expires_in: URL expiration time in seconds (default 1 hour)

        Returns:
            Presigned URL string
        """
        try:
            async with self.session.client("s3") as s3:
                url = await s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket_name, "Key": file_key},
                    ExpiresIn=expires_in,
                )

            return url

        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            raise ServiceException(f"Failed to generate presigned URL: {str(e)}")

    async def generate_presigned_upload_url(
        self,
        file_key: str,
        content_type: str = "application/octet-stream",
        expires_in: int = 3600,
    ) -> Dict[str, Any]:
        """
        Generate a presigned URL for direct client-side upload.

        Args:
            file_key: S3 object key to upload to
            content_type: MIME type of the file
            expires_in: URL expiration time in seconds (default 1 hour)

        Returns:
            Dictionary with url and fields for the upload
        """
        try:
            async with self.session.client("s3") as s3:
                response = await s3.generate_presigned_post(
                    Bucket=self.bucket_name,
                    Key=file_key,
                    Fields={"Content-Type": content_type},
                    Conditions=[["content-length-range", 0, 104857600]],  # Max 100MB
                    ExpiresIn=expires_in,
                )

            return response

        except ClientError as e:
            logger.error(f"Failed to generate presigned upload URL: {str(e)}")
            raise ServiceException(f"Failed to generate presigned upload URL: {str(e)}")

    async def copy_file(
        self, source_key: str, destination_key: str
    ) -> Dict[str, str]:
        """
        Copy a file within the same S3 bucket.

        Args:
            source_key: Source S3 object key
            destination_key: Destination S3 object key

        Returns:
            Dictionary with new file information
        """
        try:
            async with self.session.client("s3") as s3:
                copy_source = {"Bucket": self.bucket_name, "Key": source_key}

                await s3.copy_object(
                    CopySource=copy_source,
                    Bucket=self.bucket_name,
                    Key=destination_key,
                )

            logger.info(f"File copied: {source_key} -> {destination_key}")

            return {
                "file_key": destination_key,
                "bucket_name": self.bucket_name,
            }

        except ClientError as e:
            logger.error(f"Failed to copy file: {str(e)}")
            raise ServiceException(f"Failed to copy file: {str(e)}")

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to make it safe for S3.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove any path components
        filename = os.path.basename(filename)

        # Replace spaces with underscores
        filename = filename.replace(" ", "_")

        # Remove any non-alphanumeric characters except dots, dashes, and underscores
        import re

        filename = re.sub(r"[^a-zA-Z0-9._-]", "", filename)

        return filename

    async def get_folder_size(self, prefix: str) -> int:
        """
        Calculate total size of files in a folder.

        Args:
            prefix: Folder prefix

        Returns:
            Total size in bytes
        """
        try:
            files = await self.list_files(prefix=prefix)
            total_size = sum(file["size"] for file in files)
            return total_size

        except Exception as e:
            logger.error(f"Failed to calculate folder size: {str(e)}")
            raise ServiceException(f"Failed to calculate folder size: {str(e)}")
