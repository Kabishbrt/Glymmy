"""Glymmy backend entry point.

Run from the glymmy_backend/ directory:

    python main.py                   # uses .env settings
    python main.py --port 9000       # override port
    python main.py --no-reload       # disable hot reload

All defaults come from .env (copy .env.example → .env to get started).
"""

from __future__ import annotations

import argparse
import os
import sys


def _load_dotenv() -> None:
    """Load .env before importing anything that reads settings."""
    try:
        from dotenv import load_dotenv

        load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
    except ImportError:
        pass  # dotenv is optional — pydantic-settings reads .env itself


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Glymmy API server")
    parser.add_argument("--host", default=None, help="Bind host (default: from .env or 0.0.0.0)")
    parser.add_argument("--port", type=int, default=None, help="Bind port (default: from .env or 8000)")
    parser.add_argument("--no-reload", action="store_true", help="Disable hot reload")
    return parser.parse_args()


def main() -> None:
    # Ensure we're running from glymmy_backend/ so relative paths (.env, datasets) work
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    sys.path.insert(0, backend_dir)

    _load_dotenv()

    args = _parse_args()

    # Import settings after .env is loaded
    from app.core.config import get_settings

    settings = get_settings()

    host = args.host or settings.HOST
    port = args.port or settings.PORT
    reload = not args.no_reload and settings.DEBUG

    try:
        import uvicorn
    except ImportError:
        print("uvicorn not found. Run:  uv sync")
        sys.exit(1)

    print(f"\n  Glymmy API v{settings.APP_VERSION}")
    print(f"  http://{host}:{port}")
    print(f"  http://{host}:{port}/docs  (API explorer)")
    print(f"  LLM: {settings.LLM_PROVIDER}  |  CGM: {settings.CGM_PROVIDER}  |  Storage: {settings.STORAGE_PROVIDER}")
    print(f"  reload={reload}  debug={settings.DEBUG}\n")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="debug" if settings.DEBUG else "info",
    )


if __name__ == "__main__":
    main()
