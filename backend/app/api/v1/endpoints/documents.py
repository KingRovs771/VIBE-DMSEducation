"""
Document endpoints — CRUD, upload, download, search, approval
"""
from typing import Optional

from fastapi import (
    APIRouter, Depends, File, Form, HTTPException,
    Query, UploadFile, status,
)
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_active_admin
from app.models.document import DocumentAccessLevel, DocumentStatus
from app.models.user import User
from app.schemas.document import (
    DocumentCreate, DocumentList, DocumentResponse,
    DocumentSearchRequest, DocumentUpdate, DocumentApprovalRequest,
)
from app.services.document_service import DocumentService

router = APIRouter()


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    tags: str = Form(""),  # comma-separated
    access_level: DocumentAccessLevel = Form(DocumentAccessLevel.INTERNAL),
    category_id: Optional[int] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload dokumen baru ke sistem."""
    payload = DocumentCreate(
        title=title,
        description=description,
        tags=[t.strip() for t in tags.split(",") if t.strip()],
        access_level=access_level,
        category_id=category_id,
    )
    doc = await DocumentService.upload_document(db, file, payload, current_user)
    return doc


@router.get("/search", response_model=DocumentList)
async def search_documents(
    query: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    status: Optional[DocumentStatus] = Query(None),
    access_level: Optional[DocumentAccessLevel] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cari dokumen dengan filter dan full-text search."""
    params = DocumentSearchRequest(
        query=query, category_id=category_id, status=status,
        access_level=access_level, page=page, size=size,
    )
    docs, total = await DocumentService.search_documents(db, params, current_user)
    return DocumentList(items=docs, total=total, page=page, size=size)


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ambil detail dokumen by ID."""
    return await DocumentService.get_document(db, doc_id, current_user)


@router.get("/{doc_id}/download")
async def download_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download dokumen via presigned URL."""
    url = await DocumentService.get_download_url(db, doc_id, current_user)
    return RedirectResponse(url=url)


@router.patch("/{doc_id}", response_model=DocumentResponse)
async def update_document(
    doc_id: int,
    payload: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update metadata dokumen."""
    return await DocumentService.update_document(db, doc_id, payload, current_user)


@router.post("/{doc_id}/approve", response_model=DocumentResponse)
async def approve_document(
    doc_id: int,
    payload: DocumentApprovalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    """Approve atau reject dokumen (admin only)."""
    return await DocumentService.approve_document(db, doc_id, payload, current_user)


@router.delete("/{doc_id}", status_code=204)
async def delete_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Hapus dokumen."""
    await DocumentService.delete_document(db, doc_id, current_user)
