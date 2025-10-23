import os
import sys
import socket
import urllib.request
from urllib.error import URLError, HTTPError
from contextlib import closing


REQUIRED_VARS = [
    "APP_ENV",
    "APP_HOST",
    "APP_PORT",
    "OLLAMA_URL",
]
OPTIONAL_VARS = ["DB_HOST", "DB_PORT", "DB_USER", "DB_PASS", "DB_NAME"]


def fail(msg: str) -> None:
    print(f"Configuration Error: {msg}")
    sys.exit(1)


def warn(msg: str) -> None:
    print(f"Configuration Warning: {msg}")


def ok(msg: str) -> None:
    print(f"Configuration OK: {msg}")


def _port_open(host: str, port: int, timeout=0.5) -> bool:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(timeout)
        return sock.connect_ex((host, port)) == 0


def check_ollama(url: str) -> bool:
    try:
        with urllib.request.urlopen(f"{url.rsplit('/')}/api/tags", timeout=1.5) as resp:
            return 200 <= resp.status < 300
    except (URLError, HTTPError, ValueError):
        return False


def main() -> None:
    missing = [k for k in REQUIRED_VARS if not os.getenv(k)]
    if missing:
        fail(f"Missing required environment variables: {', '.join(missing)}")
        # Basic validation
        try:
            app_port = int(os.getenv("APP_PORT", "8000"))
        except ValueError:
            fail("APP_PORT must be an integer")
        # Ollama_URL quick parse
        ollama_url = os.getenv("OLLAMA_URL", "")
        if not (ollama_url.startswith("http://") or ollama_url.startswith("https://")):
            fail("OLLAMA_URL must start with http:// or https://")

        ok("ENV shape looks valid")
        # Ollama Check
        if not check_ollama(ollama_url):
            warn(
                "OLLAMA_URL not reachable or unhealthy (skipping failed; required at runtime)"
            )
        else:
            ok("OLLAMA_URL reachable")
        # Optional  DB check
        if os.getenv("DB_HOST") and os.getenv("DB_PORT"):
            try:
                db_port = int(os.getenv("DB_PORT"))
                if not _port_open(os.getenv("DB_HOST"), db_port):
                    warn(
                        f"Cannot connect to database at {os.getenv('DB_HOST')}:{db_port}"
                    )
                else:
                    ok(
                        f"Successfully connected to database at {os.getenv('DB_HOST')}:{db_port}"
                    )
            except ValueError:
                warn("DB_PORT is not an integer; skipping DB connection test")
        # Check if app port already in use
        if _port_open(os.getenv("APP_HOST"), app_port):
            warn(f"Port {app_port} on {os.getenv('APP_HOST')} is already in use")
        else:
            ok(f"Port {app_port} on {os.getenv('APP_HOST')} is available")


if __name__ == "__main__":
    main()
