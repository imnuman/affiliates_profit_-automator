"""
File upload endpoints using AWS S3.
"""
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.dependencies import get_current_user
from app.services.storage import S3StorageService
from app.core.logging import logger
from app.core.exceptions import ServiceException


router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    folder: str = Query("uploads", description="S3 folder/prefix"),
    public: bool = Query(False, description="Make file publicly accessible"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a file to S3.

    - **file**: File to upload
    - **folder**: S3 folder (uploads, bonuses, media, etc.)
    - **public**: Whether to make file publicly accessible

    Returns file URL and metadata.
    """
    try:
        # Validate file size (max 100MB)
        max_size = 100 * 1024 * 1024  # 100MB
        file_content = await file.read()

        if len(file_content) > max_size:
            raise HTTPException(
                status_code=413,
                detail="File too large. Maximum size is 100MB"
            )

        # Initialize storage service
        storage = S3StorageService()

        # Add user ID to folder path for organization
        user_folder = f"{folder}/{current_user.id}"

        # Upload file
        result = await storage.upload_file(
            file_data=file_content,
            file_name=file.filename,
            folder=user_folder,
            content_type=file.content_type,
            metadata={
                "user_id": str(current_user.id),
                "original_filename": file.filename,
                "uploaded_by": current_user.email
            },
            public=public
        )

        logger.info(f"File uploaded by user {current_user.id}: {result['file_key']}")

        return {
            "success": True,
            "file_url": result["file_url"],
            "file_key": result["file_key"],
            "bucket": result["bucket_name"],
            "file_name": file.filename,
            "size": len(file_content),
            "content_type": file.content_type
        }

    except ServiceException as e:
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during upload: {str(e)}")
        raise HTTPException(status_code=500, detail="File upload failed")


@router.post("/upload-multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    folder: str = Query("uploads", description="S3 folder/prefix"),
    public: bool = Query(False, description="Make files publicly accessible"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload multiple files to S3.

    Maximum 10 files per request.
    """
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 files per upload"
        )

    storage = S3StorageService()
    results = []
    failed = []

    user_folder = f"{folder}/{current_user.id}"

    for file in files:
        try:
            file_content = await file.read()

            # Skip files larger than 100MB
            if len(file_content) > 100 * 1024 * 1024:
                failed.append({
                    "file_name": file.filename,
                    "error": "File too large (max 100MB)"
                })
                continue

            result = await storage.upload_file(
                file_data=file_content,
                file_name=file.filename,
                folder=user_folder,
                content_type=file.content_type,
                metadata={"user_id": str(current_user.id)},
                public=public
            )

            results.append({
                "file_name": file.filename,
                "file_url": result["file_url"],
                "file_key": result["file_key"],
                "size": len(file_content)
            })

        except Exception as e:
            failed.append({
                "file_name": file.filename,
                "error": str(e)
            })

    logger.info(f"Batch upload by user {current_user.id}: {len(results)} succeeded, {len(failed)} failed")

    return {
        "success": True,
        "uploaded": len(results),
        "failed": len(failed),
        "results": results,
        "failures": failed
    }


@router.get("/presigned-upload-url")
async def get_presigned_upload_url(
    file_name: str = Query(..., description="File name"),
    content_type: str = Query("application/octet-stream", description="Content type"),
    folder: str = Query("uploads", description="S3 folder"),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a presigned URL for direct client-side upload to S3.

    This allows uploading large files directly from browser to S3 without
    going through the backend.

    Returns URL and fields for POST upload.
    """
    try:
        storage = S3StorageService()

        # Generate S3 key
        from datetime import datetime
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_key = f"{folder}/{current_user.id}/{timestamp}_{file_name}"

        # Generate presigned POST URL
        presigned_data = await storage.generate_presigned_upload_url(
            file_key=file_key,
            content_type=content_type,
            expires_in=3600  # 1 hour
        )

        return {
            "success": True,
            "upload_url": presigned_data["url"],
            "fields": presigned_data["fields"],
            "file_key": file_key,
            "expires_in": 3600
        }

    except Exception as e:
        logger.error(f"Presigned URL generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presigned-download-url")
async def get_presigned_download_url(
    file_key: str = Query(..., description="S3 file key"),
    expires_in: int = Query(3600, description="URL expiration in seconds"),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a presigned URL for downloading a private file from S3.

    - **file_key**: S3 object key
    - **expires_in**: URL expiration time in seconds (default 1 hour)
    """
    try:
        # Verify user owns this file (file key contains user ID)
        if str(current_user.id) not in file_key:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to access this file"
            )

        storage = S3StorageService()

        # Check if file exists
        exists = await storage.file_exists(file_key)
        if not exists:
            raise HTTPException(status_code=404, detail="File not found")

        # Generate presigned URL
        download_url = await storage.generate_presigned_url(
            file_key=file_key,
            expires_in=expires_in
        )

        return {
            "success": True,
            "download_url": download_url,
            "file_key": file_key,
            "expires_in": expires_in
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Presigned download URL generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete")
async def delete_file(
    file_key: str = Query(..., description="S3 file key"),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a file from S3.

    Users can only delete their own files.
    """
    try:
        # Verify user owns this file
        if str(current_user.id) not in file_key:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to delete this file"
            )

        storage = S3StorageService()

        # Delete file
        success = await storage.delete_file(file_key)

        if not success:
            raise HTTPException(status_code=500, detail="File deletion failed")

        logger.info(f"File deleted by user {current_user.id}: {file_key}")

        return {
            "success": True,
            "message": "File deleted successfully",
            "file_key": file_key
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File deletion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete-multiple")
async def delete_multiple_files(
    file_keys: List[str] = Query(..., description="List of S3 file keys"),
    current_user: User = Depends(get_current_user)
):
    """
    Delete multiple files from S3.

    Maximum 100 files per request.
    """
    if len(file_keys) > 100:
        raise HTTPException(
            status_code=400,
            detail="Maximum 100 files per deletion"
        )

    # Verify user owns all files
    for file_key in file_keys:
        if str(current_user.id) not in file_key:
            raise HTTPException(
                status_code=403,
                detail=f"You don't have permission to delete file: {file_key}"
            )

    try:
        storage = S3StorageService()

        # Delete files
        results = await storage.delete_files(file_keys)

        deleted_count = sum(1 for success in results.values() if success)

        logger.info(f"Batch deletion by user {current_user.id}: {deleted_count}/{len(file_keys)} deleted")

        return {
            "success": True,
            "deleted": deleted_count,
            "total": len(file_keys),
            "results": results
        }

    except Exception as e:
        logger.error(f"Batch file deletion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_user_files(
    folder: str = Query("uploads", description="Folder to list"),
    max_files: int = Query(100, description="Maximum files to return"),
    current_user: User = Depends(get_current_user)
):
    """
    List files uploaded by the current user.

    Returns list of files with metadata.
    """
    try:
        storage = S3StorageService()

        # List files in user's folder
        prefix = f"{folder}/{current_user.id}/"
        files = await storage.list_files(prefix=prefix, max_keys=max_files)

        return {
            "success": True,
            "count": len(files),
            "folder": folder,
            "files": files
        }

    except Exception as e:
        logger.error(f"File listing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/file-info")
async def get_file_info(
    file_key: str = Query(..., description="S3 file key"),
    current_user: User = Depends(get_current_user)
):
    """
    Get metadata for a specific file.
    """
    try:
        # Verify user owns this file
        if str(current_user.id) not in file_key:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to access this file"
            )

        storage = S3StorageService()

        # Get file metadata
        metadata = await storage.get_file_metadata(file_key)

        return {
            "success": True,
            "file_key": file_key,
            **metadata
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File info retrieval failed: {str(e)}")
        raise HTTPException(status_code=404, detail="File not found")
