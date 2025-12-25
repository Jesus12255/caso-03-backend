
from app.core.domain.document import Document
from app.core.repository.document_repository import DocumentRepository
from app.core.services.document_service import DocumentService
from config.mapper import Mapper
from dto.document import DocumentRequest



class DocumentServiceImpl(DocumentService):

    def __init__(self, document_repository: DocumentRepository):
        self.document_repository = document_repository

    async def save(self, t: DocumentRequest):
        document = Mapper.to_entity(t, Document)
        document.fields = [field.model_dump() for field in t.fields]
        document.type = t.detectedType   
        document.file_name = t.fileName
        document.is_anonymized = t.isAnonymized 
        await self.document_repository.save(document)

    async def find_all(self):
        return await self.document_repository.find_all()

    async def delete(self, id: str):
        return await self.document_repository.delete(id)

    async def update(self, id: str, t: DocumentRequest):
        return await self.document_repository.update(id, t.isAnonymized)
