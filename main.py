from config.app_logging import setup_logging
from config.router_doc_config import app
from config.cors_config import setup_cors
from config.router_config import setup_routes


setup_logging()
setup_cors(app)
setup_routes(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
