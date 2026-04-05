from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from service.upload_service import UploadService


class PresignUploadRequest(BaseModel):
    file_name: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=1, max_length=100)
    folder: str = Field(default="items", min_length=1, max_length=80)


def create_upload_routes() -> APIRouter:
    router = APIRouter(prefix="/uploads", tags=["Uploads"])
    upload_service = UploadService()

    @router.post("/presign", status_code=status.HTTP_200_OK)
    def create_presigned_upload(request: PresignUploadRequest):
        """Create an S3 presigned upload URL for an image file."""
        return upload_service.create_presigned_upload(
            file_name=request.file_name,
            content_type=request.content_type,
            folder=request.folder,
        )

    return router