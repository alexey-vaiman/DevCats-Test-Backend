import uuid
from typing import Optional, List
from fastapi import APIRouter, Query, UploadFile, File, Response, status

from app.api.deps import SessionDep, AdminDep
from app.schemas.product import AdminProductCreate, AdminProductUpdate, AdminProductResponse
from app.schemas.common import PaginatedResponse
from app.services.product_service import product_service
from app.services.s3_service import s3_service

router = APIRouter(prefix="/products", tags=["AdminProducts"])

@router.get("", response_model=PaginatedResponse[AdminProductResponse])
async def list_admin_products(
    db: SessionDep,
    _admin: AdminDep,
    limit: int = Query(50, ge=1, le=100),
    cursor: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    return await product_service.admin_get_products(db, limit=limit, cursor=cursor, search=search)

@router.post("", response_model=AdminProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: AdminProductCreate,
    db: SessionDep,
    _admin: AdminDep
):
    return await product_service.admin_create_product(db, product_in)

@router.get("/{product_id}", response_model=AdminProductResponse)
async def get_product(
    product_id: uuid.UUID,
    db: SessionDep,
    _admin: AdminDep
):
    return await product_service.admin_get_product(db, product_id)

@router.put("/{product_id}", response_model=AdminProductResponse)
async def update_product(
    product_id: uuid.UUID,
    product_in: AdminProductUpdate,
    db: SessionDep,
    _admin: AdminDep
):
    return await product_service.admin_update_product(db, product_id, product_in)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: uuid.UUID,
    db: SessionDep,
    _admin: AdminDep
):
    await product_service.admin_delete_product(db, product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

import io
from PIL import Image

@router.post("/{product_id}/image")
async def upload_product_image(
    product_id: uuid.UUID,
    db: SessionDep,
    _admin: AdminDep,
    file: UploadFile = File(...)
):
    file_bytes = await file.read()
    
    # Upload original
    original_url = s3_service.upload_file(file_bytes, file.filename, content_type=file.content_type)
    
    # Generate thumbnail
    try:
        img = Image.open(io.BytesIO(file_bytes))
        # Convert to RGB if necessary (e.g. for PNG with alpha to JPEG, though we keep original format if possible)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        img.thumbnail((200, 200)) # Maintain aspect ratio
        
        thumb_io = io.BytesIO()
        img.save(thumb_io, format="JPEG", quality=85)
        thumb_bytes = thumb_io.getvalue()
        
        # Determine thumbnail filename
        ext = file.filename.split('.')[-1]
        thumb_filename = f"thumb_{file.filename}"
        
        thumb_url = s3_service.upload_file(thumb_bytes, thumb_filename, content_type="image/jpeg")
    except Exception as e:
        print(f"Thumbnail generation failed: {e}")
        thumb_url = original_url # Fallback to original if processing fails
    
    product = await product_service.admin_update_product_images(db, product_id, original_url, thumb_url)
    
    return {"image_url": product.image_url, "thumbnail_url": product.thumbnail_url}
