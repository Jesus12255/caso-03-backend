import json
import asyncio
import google.generativeai as genai
from app.integration.extraction_engine import ExtractionEngine
from config.config import settings

# Configure Gemini once
genai.configure(api_key=settings.LLM_API_KEY)

class ExtractionEngineImpl(ExtractionEngine):

    async def extract_single_page(self, base64_image: str, page_index: int) -> dict:
        model = genai.GenerativeModel(settings.LLM_MODEL_NAME)
        
        # Simplified prompt for single image
        prompt = f"""Analiza esta imagen (Página {page_index}). Extrae TODOS los datos, tablas y campos en formato JSON estructurado.

Formato requerido:
{{
  "document_index": {page_index},
  "document_name": "GENERAR UN NOMBRE CORTO Y DESCRIPTIVO BASADO EN EL CONTENIDO (Ej: Factura #123 Acme, Contrato de Arrendamiento)",
  "fields": {{
    "campo": "valor"
  }}
}}

NO inventes datos. Si es ilegible, reporta null."""

        contents = [
            prompt,
            {"mime_type": "image/jpeg", "data": base64_image} # Assuming jpeg from pdf conversion or raw
        ]

        # Optimized Retry Logic: Faster backoff for parallel requests
        max_retries = 3
        retry_delay = 2 # Start with 2 seconds
        
        for attempt in range(max_retries):
            try:
                response = await model.generate_content_async(
                    contents,
                    generation_config={"response_mime_type": "application/json"}
                )
                
                # Parse immediately to ensure valid JSON
                if response.text:
                    return json.loads(response.text)
                else:
                    return {"document_index": page_index, "error": "Empty response"}

            except Exception as e:
                error_str = str(e)
                if "FreeTier" in error_str or "PerDay" in error_str:
                     print(f"Daily Quota Exceeded on page {page_index}: {e}")
                     raise e

                # Rate Limit -> Retry
                if "429" in error_str or "ResourceExhausted" in error_str:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2 # Exponential backoff: 2, 4, 8...
                        continue
                
                # If we're here, it's a non-retriable error or max retries exceeded
                print(f"Error processing page {page_index}: {e}")
                return {"document_index": page_index, "error": str(e)}
        
        return {"document_index": page_index, "error": "Max retries exceeded"}

    async def extract_stream(self, base64_images: list[str]):
        # Legacy/Sequential implementation - kept for interface compatibility or fallback
        model = genai.GenerativeModel(settings.LLM_MODEL_NAME)
        # ... (rest of old implementation if needed, or just warn)
        # For this task, we assume the service will switch to extract_single_page.
        pass