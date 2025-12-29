import asyncio
import base64
from io import BytesIO
import fitz
import json

class MockExtractionEngine:
    async def extract_single_document(self, base64_data, mime_type, page_count, start_index):
        # Return a mock list of results
        return [
            {
                "document_index": start_index + i,
                "document_name": f"Mock Page {start_index + i}",
                "fields": {"test": "data"}
            } for i in range(page_count)
        ]

async def test_logic():
    print("Testing page counting and flattening logic...")
    
    # Create a real 2-page PDF in memory using fitz
    doc = fitz.open()
    doc.new_page()
    doc.new_page()
    pdf_bytes = doc.tobytes()
    doc.close()
    
    print(f"Created dummy PDF with {len(pdf_bytes)} bytes.")
    
    # Mocking the service logic
    from app.core.services.impl.analyze_service_impl import AnalyzeServiceImpl
    engine = MockExtractionEngine()
    service = AnalyzeServiceImpl(engine)
    
    files_data = [
        {"filename": "test.pdf", "content": pdf_bytes}
    ]
    
    print("Running upload_stream...")
    async for event in service.upload_stream(files_data):
        if "response" in event:
            import json
            # Event format is "data: {...}\n\n"
            data_str = event.replace("data: ", "").strip()
            result = json.loads(data_str)
            if "response" in result:
                response_data = json.loads(result["response"])
                print("Final Response Documents:")
                for doc in response_data["documents"]:
                    print(f"  - Index: {doc['document_index']}, Name: {doc['document_name']}")
                
                if len(response_data["documents"]) == 2:
                    print("SUCCESS: Found 2 documents for 2 pages.")
                else:
                    print(f"FAILURE: Found {len(response_data['documents'])} documents.")

if __name__ == "__main__":
    asyncio.run(test_logic())
