import os
import signal
import sys
from typing import Optional

import uvicorn

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))
from src.config import Config
from src.server import create_app
from src.state import AppState


def init_state(config: Config) -> Optional[AppState]:
    """Initialize application state"""
    try:
        state = AppState.from_config(config)
        print("✓ Application state initialized")
        return state
    except Exception as e:
        print(f"✗ Failed to initialize application state: {e}")
        return None


# Initialize app for production use
config = Config()
print(f"config: {config}")
state = init_state(config)
app = create_app(state) if state else None


def main() -> int:
    """Main entrypoint for the server"""

    def signal_handler(signum: int, frame: object) -> None:
        print(f"\n✓ Received signal {signum}, shutting down...")
        sys.exit(0)

    # Handle SIGINT (Ctrl+C) and SIGTERM gracefully
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        if not state or not app:
            print("✗ Failed to initialize application")
            return 1

        print("✓ Configuration loaded from environment")
        print("✓ FastAPI application created")

        print(f"Starting server on {config.listen_address}:{config.listen_port}")

        if config.dev_mode:
            uvicorn.run(
                "src.__main__:app",
                host=config.listen_address,
                port=config.listen_port,
                proxy_headers=True,
                reload=True,
                reload_dirs=["src", "templates", "static"],
            )
        else:
            uvicorn.run(
                app,
                host=config.listen_address,
                port=config.listen_port,
                proxy_headers=True,
            )
        return 0
    except KeyboardInterrupt:
        print("\n✓ Server stopped by user")
        return 0
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
