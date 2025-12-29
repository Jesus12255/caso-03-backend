from typing import List
from fastapi import APIRouter, Depends

from app.core.dependencies.dependencies_document import get_document_facade
from app.core.facade.document_facade import DocumentFacade
from dto.document import DocumentRequest
from dto.universal_dto import BaseOperacionResponse

router = APIRouter()

@router.post("/save", response_model=BaseOperacionResponse)
async def save( requestList: List[DocumentRequest], document_facade: DocumentFacade = Depends(get_document_facade)) -> BaseOperacionResponse:
    return await document_facade.save(requestList)

@router.get("/list", response_model=List[dict])
async def list_documents(document_facade: DocumentFacade = Depends(get_document_facade)):
    return await document_facade.list()

@router.delete("/delete/{id}", response_model=BaseOperacionResponse)
async def delete_document(id: str, document_facade: DocumentFacade = Depends(get_document_facade)):
    return await document_facade.delete(id)

@router.put("/update/{id}", response_model=BaseOperacionResponse)
async def update_document(id: str, request: DocumentRequest, document_facade: DocumentFacade = Depends(get_document_facade)):
    return await document_facade.update(id, request)