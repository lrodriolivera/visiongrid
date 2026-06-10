from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="visiongrid",
        description="VisionGrid — Open-source real-time computer vision platform",
    )
    subparsers = parser.add_subparsers(dest="command")

    serve_parser = subparsers.add_parser("serve", help="Start the VisionGrid server")
    serve_parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    serve_parser.add_argument("--config", type=Path, help="Path to config file")
    serve_parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    serve_parser.add_argument(
        "--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"]
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "serve":
        _run_server(args)


def _run_server(args: argparse.Namespace) -> None:
    import os

    import uvicorn

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    if args.config:
        os.environ["VISIONGRID_CONFIG_PATH"] = str(args.config.resolve())

    uvicorn.run(
        "visiongrid.api.app:create_app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        factory=True,
        log_level=args.log_level.lower(),
    )


if __name__ == "__main__":
    main()
