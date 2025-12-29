from abc import ABC, abstractmethod


class ExtractionEngine(ABC):

    @abstractmethod
    async def extract_stream(self, documents_data: list[dict]) -> dict:
        pass

    @abstractmethod
    async def extract_single_document(self, base64_data: str, mime_type: str, page_count: int, start_index: int) -> list[dict]:
        pass

