import asyncio
import os
import google.generativeai as genai
from app.integration.impl.extraction_engine_impl import ExtractionEngineImpl

# Dummy base64 image (1x1 red pixel)
DUMMY_IMAGE = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

async def verify():
    print("Initializing ExtractionEngineImpl...")
    engine = ExtractionEngineImpl()
    
    print(f"Using model: {engine.model_name if hasattr(engine, 'model_name') else 'Unknown'}")
    
    full_text = ""
    try:
        print("Calling extract_stream with dummy image...")
        
        async for chunk in engine.extract_stream([DUMMY_IMAGE]):
             full_text += chunk
             print(".", end="", flush=True)

        print("\nStream finished.")
        print("-" * 20)
        print(full_text)
        print("-" * 20)
        
        with open("final_result.txt", "w", encoding="utf-8") as f:
            f.write(full_text)
            
    except Exception as e:
        print(f"\nFinal Error received: {e}")
        with open("final_error.txt", "w", encoding="utf-8") as f:
            f.write(str(e))

if __name__ == "__main__":
    asyncio.run(verify())
