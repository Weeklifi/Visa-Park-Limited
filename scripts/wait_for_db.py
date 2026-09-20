"""Block until the configured Postgres host accepts TCP connections.

Docker Compose's `depends_on: condition: service_healthy` only orders startup for
`docker compose up`. When the Docker daemon restarts (machine reboot, Docker Desktop
relaunch), it restarts `restart: unless-stopped` containers in arbitrary order and
ignores `depends_on` — so the API can start before Postgres or even before the compose
network's DNS is ready, and `alembic upgrade head` dies with a name-resolution error.
Running this first makes the API wait it out instead of crash-looping.
"""

import os
import socket
import sys
import time
from urllib.parse import urlparse


def target() -> tuple[str, int]:
    parsed = urlparse(os.environ.get("DATABASE_URL", ""))
    return parsed.hostname or "postgres", parsed.port or 5432


def main() -> int:
    host, port = target()
    timeout = float(os.environ.get("DB_WAIT_TIMEOUT", "120"))
    deadline = time.monotonic() + timeout
    attempt = 0

    while time.monotonic() < deadline:
        attempt += 1
        try:
            with socket.create_connection((host, port), timeout=2):
                print(f"Postgres reachable at {host}:{port} (attempt {attempt})", flush=True)
                return 0
        except OSError as exc:
            print(f"  waiting for {host}:{port} — {exc} (attempt {attempt})", flush=True)
            time.sleep(2)

    print(f"Timed out after {timeout:.0f}s waiting for {host}:{port}", flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(main())
