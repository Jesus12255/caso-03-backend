from abc import ABC, abstractmethod


class ExtractionEngine(ABC):

    @abstractmethod
    async def extract_stream(self, base64_images: list[str]) -> dict:
        pass

    @abstractmethod
    async def extract_single_page(self, base64_image: str, page_index: int) -> dict:
        pass