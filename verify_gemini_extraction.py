import asyncio
import os
from app.integration.impl.extraction_engine_impl import ExtractionEngineImpl

# Dummy base64 image (1x1 red pixel)
DUMMY_IMAGE = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

async def verify():
    print("Initializing ExtractionEngineImpl...")
    engine = ExtractionEngineImpl()
    
    print("Calling extract_stream with dummy image...")
    try:
        async for chunk in engine.extract_stream([DUMMY_IMAGE]):
            print(f"Received chunk: {chunk}", end="", flush=True)
        print("\n\nStream finished successfully.")
    except Exception as e:
        print(f"\nError received: {e}")

if __name__ == "__main__":
    asyncio.run(verify())
