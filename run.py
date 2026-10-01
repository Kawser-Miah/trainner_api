"""Run the FastAPI application.

Usage:
    python run.py
    python run.py --port 8080
"""

import uvicorn
from src.core.config import settings
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Couch Hub FastAPI Application")
    parser.add_argument("--host", default=settings.host, help="Host address")
    parser.add_argument("--port", type=int, default=settings.port, help="Port number")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    if args.reload:
        print("⚠️  Auto-reload enabled (development mode)")
    print(f"Starting server on {args.host}:{args.port}")
    
    uvicorn.run(
        "src.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )