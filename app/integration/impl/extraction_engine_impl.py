import json
import asyncio
import google.generativeai as genai
from app.integration.extraction_engine import ExtractionEngine
from config.config import settings

# Configure Gemini once
genai.configure(api_key=settings.LLM_API_KEY)

class ExtractionEngineImpl(ExtractionEngine):

    async def extract_single_document(self, base64_data: str, mime_type: str, page_count: int, start_index: int) -> list[dict]:
        model = genai.GenerativeModel(settings.LLM_MODEL_NAME)
        
        # Enhanced prompt for multi-page document extraction
        prompt = f"""Analiza este documento por completo ({page_count} páginas). 
Debes extraer TODOS los datos, tablas y campos de CADA PÁGINA por separado.

Es CRITICO que devuelvas exactamente una lista (array) de JSON, donde cada objeto represente una página física del documento.

Formato requerido:
[
  {{
    "document_index": {start_index}, 
    "document_name": "Nombre descriptivo página 1",
    "fields": {{ "campo": "valor" }}
  }},
  ... y así sucesivamente para las {page_count} páginas, incrementando el document_index.
]

Si una página es ilegible, devuelve el objeto igualmente con campos null. NO inventes datos."""

        contents = [
            prompt,
            {"mime_type": mime_type, "data": base64_data}
        ]

        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = await model.generate_content_async(
                    contents,
                    generation_config={"response_mime_type": "application/json"}
                )
                
                if response.text:
                    result_data = json.loads(response.text)
                    # Force result to be a list if LLM returns a single object
                    if isinstance(result_data, dict):
                        return [result_data]
                    return result_data
                else:
                    return [{"document_index": start_index, "error": "Empty response"}]

            except Exception as e:
                error_str = str(e)
                if "FreeTier" in error_str or "PerDay" in error_str:
                     print(f"Daily Quota Exceeded: {e}")
                     raise e

                if "429" in error_str or "ResourceExhausted" in error_str:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2
                        continue
                
                print(f"Error processing documents starting at {start_index}: {e}")
                return [{"document_index": start_index, "error": str(e)}]
        
        return [{"document_index": start_index, "error": "Max retries exceeded"}]


    async def extract_stream(self, documents_data: list[dict]):
        # Updated to match interface, though AnalyzeServiceImpl now uses extract_single_document directly in parallel
        pass
