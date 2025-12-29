from typing import List
from app.core.facade.document_facade import DocumentFacade
from app.core.services.document_service import DocumentService
from dto.document import DocumentRequest
from dto.universal_dto import BaseOperacionResponse


class DocumentFacadeImpl(DocumentFacade):

    def __init__(self, document_service: DocumentService):
        self.document_service = document_service

    async def save(self, t: List[DocumentRequest]) -> BaseOperacionResponse:
        try:
            for tt in t:
                await self.document_service.save(tt)
            return BaseOperacionResponse(codigo="200", mensaje="Documentos guardados correctamente")
        except Exception as e:
            print(f"DEBUG: Error in facade save: {e}")
            return BaseOperacionResponse(codigo="500", mensaje=f"Error al guardar documentos: {e}")

    async def list(self) -> List[dict]:
        docs = await self.document_service.find_all()
        # Transform entity to dictionary/DTO
        return [
            {
                "id": str(doc.document_id),
                "fileName": doc.file_name,
                "detectedType": doc.type,
                "fields": doc.fields,
                "created": doc.created.strftime("%Y-%m-%d %H:%M:%S") if doc.created else None,
                "isEncrypted": doc.is_anonymized # Assuming using same flag
            }
            for doc in docs
        ]

    async def delete(self, id: str) -> BaseOperacionResponse:
        try:
            success = await self.document_service.delete(id)
            if success:
                return BaseOperacionResponse(codigo="200", mensaje="Documento eliminado")
            return BaseOperacionResponse(codigo="404", mensaje="Documento no encontrado")
        except Exception as e:
             return BaseOperacionResponse(codigo="500", mensaje=f"Error al eliminar: {e}")

    async def update(self, id: str, request: DocumentRequest) -> BaseOperacionResponse:
        try:
            success = await self.document_service.update(id, request)
            if success:
                return BaseOperacionResponse(codigo="200", mensaje="Documento actualizado")
            return BaseOperacionResponse(codigo="404", mensaje="Documento no encontrado o no modificado")
        except Exception as e:
            return BaseOperacionResponse(codigo="500", mensaje=f"Error al actualizar: {e}")