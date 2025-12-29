import asyncio
import base64
import os
import sys

# Add current directory to path to import app
sys.path.append(os.getcwd())

from app.integration.impl.extraction_engine_impl import ExtractionEngineImpl
from config.config import settings

async def verify():
    print(f"Using Model: {settings.LLM_MODEL_NAME}")
    engine = ExtractionEngineImpl()
    
    # Simple dummy PDF header
    dummy_pdf_base64 = "JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAyMQo+PgpzdHJlYW0KQlQgL0YxIDI0IFRmIDEwMCAxMDAgVGQgKEhlbGxvIFdvcmxkKSBUaiBFVAplbmRzdHJlYW0KZW5kb2JqCnRyYWlsZXIKPDwKL1Jvb3QgMSAwIFIKL1NpemUgNQo+Pgp%%EOF"
    
    page_count = 2 # Testing multi-page logic
    start_idx = 1
    
    print(f"Testing extract_single_document with {page_count} pages starting at {start_idx}...")
    try:
        results = await engine.extract_single_document(dummy_pdf_base64, "application/pdf", page_count, start_idx)
        print("Results received:")
        import json
        print(json.dumps(results, indent=2))
        
        if isinstance(results, list):
            print(f"Success! Received a list of {len(results)} items.")
            if len(results) > 0 and "error" in results[0]:
                print(f"Note: Potential error in first result: {results[0]['error']}")
        else:
            print("Warning: Expected a list but received a single object.")
            
    except Exception as e:
        print(f"Error during verification: {e}")


if __name__ == "__main__":
    asyncio.run(verify())
