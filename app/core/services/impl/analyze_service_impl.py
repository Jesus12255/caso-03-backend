import base64
from io import BytesIO
import fitz
from typing import Any, Dict, List
from fastapi import UploadFile

from app.core.services.analyze_service import AnalyzeService
from app.integration.extraction_engine import ExtractionEngine
from core.exceptions import AppBaseException
from utl.file_util import FileUtil


class AnalyzeServiceImpl(AnalyzeService):

    def __init__(self, extraction_engine: ExtractionEngine):
        self.extraction_engine = extraction_engine


    # --------------------------
    #   UPLOAD NORMAL (no stream)
    # --------------------------
    async def upload(self, t: List[UploadFile]) -> List[Dict[str, Any]]:
        results = []

        for file in t:
            content = await file.read()                       
            pages = self.to_base64_from_bytes(content, file.filename)

            if not pages:
                raise AppBaseException(
                    message=f"El archivo {file.filename} está corrupto, vacío o tiene un formato no soportado."
                )
            
            file_extracted_data = []
            for idx, page_img in enumerate(pages):
                data = await self.extraction_engine.extract_data_from_image(page_img)
                file_extracted_data.append({
                    "page": idx + 1,
                    "content": data
                })

            results.append({
                "filename": file.filename,
                "total_pages": len(pages),
                "data": file_extracted_data
            })

        return results


    # --------------------------
    #   UPLOAD STREAMING
    # --------------------------
    async def upload_stream(self, files_data: List[Dict[str, Any]]):
        all_pages = []
        total_files = len(files_data)

        # 1. Procesar todos los archivos y acumular páginas
        for idx, file_data in enumerate(files_data):
            filename = file_data.get("filename")
            content = file_data.get("content")
            
            yield f"data: Procesando archivo {idx + 1}/{total_files}: {filename}...\n\n"

            pages = self.to_base64_from_bytes(content, filename)

            if not pages:
                yield f"data: [ERROR] Archivo {filename} inválido o vacío\n\n"
                continue

            all_pages.extend(pages)

        # 2. Enviar todas las imágenes al motor de extracción en una sola petición
        if not all_pages:
             yield "data: [ERROR] No se encontraron imágenes válidas para analizar.\n\n"
             return

        yield f"data: Iniciando análisis con IA de {len(all_pages)} páginas en total...\n\n"

        async for token in self.extraction_engine.extract_stream(all_pages):
            yield f"data: {token}\n\n"

        yield "data: [OK] Análisis completado.\n\n"


    # --------------------------
    #   Helper: convertir a base64 desde bytes
    # --------------------------
    def to_base64_from_bytes(self, content: bytes, filename: str) -> List[str]:
        base64_results = []

        # 📌 Validación PDF
        if FileUtil.is_valid_pdf(content):
            try:
                doc = fitz.open(stream=BytesIO(content), filetype="pdf")
                for page in doc:
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    img_bytes = pix.tobytes("jpeg")
                    base64_results.append(base64.b64encode(img_bytes).decode("utf-8"))
                doc.close()

            except Exception as e:
                print(f"Error procesando PDF: {e}")
                return []

        # 📌 Validación Imagen
        elif FileUtil.is_valid_image(content):
            base64_results.append(base64.b64encode(content).decode("utf-8"))

        return base64_results
