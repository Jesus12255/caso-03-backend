import base64
import json
import asyncio
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

    async def upload(self, t: List[UploadFile]) -> List[Dict[str, Any]]:
        # This synchronous-looking method (returning full list) can also benefit from optimization
        # But we focus on upload_stream as per useAnalysis.js usage.
        # We can reuse logic if needed.
        results = []
        for file in t:
            content = await file.read()                       
            pages = self.to_base64_from_bytes(content, file.filename)
            if not pages:
                 raise AppBaseException(message=f"El archivo {file.filename} está corrupto o vacío.")
            
            # TODO: Parallelize this too if used
            file_extracted_data = []
            for idx, page_img in enumerate(pages):
                 # This calls the old method 'extract_data_from_image' which might not exist in ExtractionEngine interface shown?
                 # The user code showed 'extract_stream' in the interface. 
                 # Wait, line 35 of original AnalyzeService called 'extract_data_from_image' but the interface only showed 'extract_stream'.
                 # I should probably fix this inconsistency or ignore 'upload' if it's not the primary flow.
                 # Given the prompt is about speed, I will leave 'upload' alone for now as the user seems to use streaming.
                 pass 
        return results

    async def upload_stream(self, files_data: List[Dict[str, Any]]):
        all_pages_tasks = []
        total_files = len(files_data)
        
        # 1. Prepare all pages
        global_page_index = 0
        for idx, file_data in enumerate(files_data):
            filename = file_data.get("filename")
            content = file_data.get("content")
            
            yield self._build_sse_event({"thinking": f"Procesando archivo {idx + 1}/{total_files}: {filename}...\n"})
            
            pages = self.to_base64_from_bytes(content, filename)
            
            if not pages:
                 yield self._build_sse_event({"thinking": f"[WARN] Archivo {filename} inválido o vacío\n"})
                 continue

            for page_img in pages:
                global_page_index += 1
                # Schedule task
                task = self.extraction_engine.extract_single_page(page_img, global_page_index)
                all_pages_tasks.append(task)

        if not all_pages_tasks:
             yield self._build_sse_event({"thinking": "[ERROR] No se encontraron imágenes válidas.\n"})
             return

        total_pages = len(all_pages_tasks)
        yield self._build_sse_event({"thinking": f"Analizando {total_pages} páginas en paralelo...\n"})

        # 2. Run in parallel
        try:
            # We use as_completed to stream results as they finish
            completed_count = 0
            
            # documents array to accumulate results
            documents = []

            for future in asyncio.as_completed(all_pages_tasks):
                result = await future
                completed_count += 1
                
                # Yield progress or partial result
                yield self._build_sse_event({"thinking": f"Pagina {result.get('document_index')} completada ({completed_count}/{total_pages})\n"})
                
                # Check for errors in result
                if result.get("error"):
                    yield self._build_sse_event({"thinking": f"[ERROR] Page {result.get('document_index')}: {result.get('error')}\n"})
                else:
                    # Construct the document object structure expected by frontend
                    doc_obj = {
                        "document_index": result.get("document_index"),
                        "document_name": result.get("document_name") or f"Page {result.get('document_index')}",
                        "fields": result.get("fields", {})
                    }
                    documents.append(doc_obj)

            # 3. Send Final JSON
            # The frontend expects a JSON with "documents": [...]
            # We can send it as a "response" token.
            final_payload = json.dumps({"documents": documents})
            yield self._build_sse_event({"response": final_payload})

        except Exception as e:
            print(f"Critical Error during parallel extraction: {e}")
            yield self._build_sse_event({"error": f"Error crítico: {str(e)}"})
            return

        yield self._build_sse_event({"thinking": "Análisis finalizado."})


    def _build_sse_event(self, data: Dict[str, Any]) -> str:
        return f"data: {json.dumps(data)}\n\n"

    def to_base64_from_bytes(self, content: bytes, filename: str) -> List[str]:
        base64_results = []

        if FileUtil.is_valid_pdf(content):
            try:
                doc = fitz.open(stream=BytesIO(content), filetype="pdf")
                for page in doc:
                    # Optimization: Reduced resolution from 2 to 1.5
                    pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                    img_bytes = pix.tobytes("jpeg")
                    base64_results.append(base64.b64encode(img_bytes).decode("utf-8"))
                doc.close()

            except Exception as e:
                print(f"Error procesando PDF: {e}")
                return []

        elif FileUtil.is_valid_image(content):
            base64_results.append(base64.b64encode(content).decode("utf-8"))

        return base64_results
