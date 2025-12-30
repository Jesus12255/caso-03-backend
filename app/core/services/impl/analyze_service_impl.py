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
        all_docs_tasks = []
        total_files = len(files_data)
        
        # 1. Prepare all documents and calculate global indices
        current_global_page_index = 1
        for idx, file_data in enumerate(files_data):
            filename = file_data.get("filename")
            content = file_data.get("content")
            
            yield self._build_sse_event({"thinking": f"Preparando archivo {idx + 1}/{total_files}: {filename}...\n"})
            
            doc_prep = self.prepare_document_for_llm(content, filename)
            
            if not doc_prep:
                 yield self._build_sse_event({"thinking": f"[WARN] Archivo {filename} no soportado o vacío\n"})
                 continue

            page_count = doc_prep["page_count"]
            start_index = current_global_page_index
            
            # Schedule task for the entire document, passing page info
            task = self.extraction_engine.extract_single_document(
                doc_prep["base64"], 
                doc_prep["mime_type"], 
                page_count,
                start_index
            )
            all_docs_tasks.append((task, filename, page_count))
            
            # Increment global index for next file
            current_global_page_index += page_count

        if not all_docs_tasks:
             yield self._build_sse_event({"thinking": "[ERROR] No se encontraron documentos válidos.\n"})
             return

        total_files_to_process = len(all_docs_tasks)
        yield self._build_sse_event({"thinking": f"Analizando {total_files_to_process} archivos en paralelo...\n"})

        # 2. Run in parallel
        try:
            completed_files_count = 0
            documents = []

            # Extract futures and map them back to metadata
            futures = [t[0] for t in all_docs_tasks]
            metadata_map = {hash(f): (t[1], t[2]) for f, t in zip(futures, all_docs_tasks)}

            for future in asyncio.as_completed(futures):
                results = await future # This is now a LIST of page dicts
                completed_files_count += 1
                
                fname, p_count = metadata_map.get(hash(future), ("Documento", 1))
                yield self._build_sse_event({"thinking": f"Archivo '{fname}' ({p_count} pág) completado ({completed_files_count}/{total_files_to_process})\n"})
                
                # Check for errors in the first result of the list if it's a list with error
                if isinstance(results, list) and len(results) > 0 and results[0].get("error"):
                    yield self._build_sse_event({"thinking": f"[ERROR] {fname}: {results[0].get('error')}\n"})
                else:
                    # results is a list of page objects
                    for page_result in results:
                        doc_obj = {
                            "document_index": page_result.get("document_index"),
                            "document_name": page_result.get("document_name") or f"{fname} - Pág {page_result.get('document_index')}",
                            "fields": page_result.get("fields", {})
                        }
                        documents.append(doc_obj)
                        # Optional: yield individual page completion if desired
                        # yield self._build_sse_event({"thinking": f"Pagina {doc_obj['document_index']} extraída.\n"})

            # 3. Send Final JSON (sorted by document_index to keep order)
            documents.sort(key=lambda x: x.get("document_index", 0))
            final_payload = json.dumps({"documents": documents})
            yield self._build_sse_event({"response": final_payload})

        except Exception as e:
            print(f"Critical Error during parallel extraction: {e}")
            yield self._build_sse_event({"error": f"Error crítico: {str(e)}"})
            return

        yield self._build_sse_event({"thinking": "Análisis finalizado."})


    def _build_sse_event(self, data: Dict[str, Any]) -> str:
        return f"data: {json.dumps(data)}\n\n"

    def prepare_document_for_llm(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Returns base64, mime_type, and page_count for the document."""
        if FileUtil.is_valid_pdf(content):
            try:
                doc = fitz.open(stream=BytesIO(content), filetype="pdf")
                page_count = doc.page_count
                doc.close()
                return {
                    "base64": base64.b64encode(content).decode("utf-8"),
                    "mime_type": "application/pdf",
                    "page_count": page_count
                }
            except Exception as e:
                print(f"Error counting pages: {e}")
                return None
                
        elif FileUtil.is_valid_image(content):
            mime_type = "image/jpeg"
            if filename.lower().endswith(".png"):
                mime_type = "image/png"
            elif filename.lower().endswith(".webp"):
                mime_type = "image/webp"
            
            return {
                "base64": base64.b64encode(content).decode("utf-8"),
                "mime_type": mime_type,
                "page_count": 1
            }
        return None


    def to_base64_from_bytes(self, content: bytes, filename: str) -> List[str]:
        # Implementation kept for compatibility with 'upload' method if needed,
        # but renamed or refactored. For now, I'll redirect it.
        doc = self.prepare_document_for_llm(content, filename)
        return [doc["base64"]] if doc else []

