import asyncio
import json

# Mock extraction engine
class MockEngine:
    async def extract_stream(self, images):
        yield "{"
        yield "\"key\": "
        yield "\"value\""
        yield "}"

# Mock service (simplified)
async def mock_upload_stream():
    # Mimic _build_sse_event logic
    def _build(d): return f"data: {json.dumps(d)}\n\n"

    yield _build({"thinking": "Iniciando análisis..."})
    
    engine = MockEngine()
    async for token in engine.extract_stream([]):
        yield _build({"response": token})
        
    yield _build({"thinking": "Análisis completado."})

async def main():
    print("Testing stream format...")
    async for chunk in mock_upload_stream():
        print(f"Received chunk: {repr(chunk)}")
        # Verify it parses as expected by frontend
        if chunk.startswith("data: "):
            json_str = chunk[6:].strip()
            try:
                data = json.loads(json_str)
                if "response" in data:
                    print(f"  -> Valid JSON with response: {data['response']}")
                elif "thinking" in data:
                    print(f"  -> Valid JSON with thinking: {data['thinking']}")
                else:
                    print(f"  -> Valid JSON but unknown fields: {data.keys()}")
            except json.JSONDecodeError as e:
                print(f"  -> Invalid JSON: {e}")

if __name__ == "__main__":
    asyncio.run(main())
