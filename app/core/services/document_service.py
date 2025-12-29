from abc import ABC, abstractmethod

from dto.document import DocumentRequest
from dto.universal_dto import BaseOperacionResponse


class DocumentService(ABC):

    @abstractmethod
    async def save(self, request: DocumentRequest):
        pass

    @abstractmethod
    async def find_all(self):
        pass

    @abstractmethod
    async def delete(self, id: str):
        pass

    @abstractmethod
    async def update(self, id: str, request: DocumentRequest):
        pass

    @abstractmethod
    async def update(self, id: str, request: DocumentRequest):
        pass