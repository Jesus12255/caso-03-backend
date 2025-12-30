import asyncio
import base64
import os
import sys
import json

# Add current directory to path
sys.path.append(os.getcwd())

from app.integration.impl.extraction_engine_impl import ExtractionEngineImpl
from config.config import settings

async def verify_image():
    print(f"Testing image extraction with model: {settings.LLM_MODEL_NAME}")
    engine = ExtractionEngineImpl()
    
    # Simple 1x1 black JPEG pixel
    dummy_image_base64 = "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAABAAEDAREAAhEBAxEB/8QAFAABAAAAAAAAAAAAAAAAAAAAAP/EABQQAQAAAAAAAAAAAAAAAAAAAAD/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8AVf/Z"
    
    print("Calling extract_single_document with image/jpeg...")
    try:
        results = await engine.extract_single_document(dummy_image_base64, "image/jpeg", 1, 1)
        print("Results received:")
        print(json.dumps(results, indent=2))
        
        if isinstance(results, list) and len(results) > 0:
            if "error" in results[0]:
                 print(f"Error returned by LLM: {results[0]['error']}")
            else:
                 print("Success! Image processed correctly.")
        else:
            print("Failure: Received empty results or non-list format.")
            
    except Exception as e:
        print(f"Error during image verification: {e}")

if __name__ == "__main__":
    asyncio.run(verify_image())
