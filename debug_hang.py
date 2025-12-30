import time
import sys

def debug_import(module_path):
    print(f"Importing {module_path}...", end="", flush=True)
    start = time.time()
    try:
        if "." in module_path:
            pkg, mod = module_path.rsplit(".", 1)
            parent = __import__(pkg, fromlist=[mod])
            getattr(parent, mod)
        else:
            __import__(module_path)
        print(f" OK ({time.time() - start:.2f}s)")
    except Exception as e:
        print(f" FAIL: {e}")

if __name__ == "__main__":
    # Test core configs
    debug_import("config.config")
    debug_import("config.database_config")
    debug_import("config.app_logging")
    debug_import("config.cors_config")
    
    # Test routers (this usually drags in services)
    debug_import("app.core.api.analyze_router")
    debug_import("app.core.api.document_router")
    debug_import("app.auth.api.router")
    
    # Finally main
    debug_import("main")
