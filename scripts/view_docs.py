#!/usr/bin/env python3
"""
@file view_docs.py
@brief A script to serve and view generated Doxygen documentation locally.
@details Starts a lightweight HTTP server in the documentation output directory,
         dynamically finds an open port, and automatically opens the user's default
         web browser.
"""

import http.server
import os
import socketserver
import sys
import threading
import time
import webbrowser

## The path to the generated HTML documentation.
DOC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "build", "doc", "html"))


def find_free_port(startPort: int = 8080, maxPort: int = 8180) -> int:
    """
    @brief Finds an available port on localhost to start the HTTP server.
    @param startPort The starting port index to probe.
    @param maxPort The maximum port index to probe.
    @return The first detected free port index.
    @raises OSError if no free port is found in the specified range.
    """
    import socket

    for port in range(startPort, maxPort):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise OSError(f"Could not find an available port in range {startPort}-{maxPort}.")


def open_browser_after_delay(url: str, delaySeconds: float = 0.5) -> None:
    """
    @brief Opens the browser to the specified URL after a brief delay.
    @param url The URL to navigate to in the browser.
    @param delaySeconds The delay in seconds before triggering the browser open.
    """
    time.sleep(delaySeconds)
    print(f"\n[info] Opening browser to {url} ...")
    webbrowser.open(url)


def main() -> None:
    """
    @brief Main entry point to serve the documentation.
    @details Configures the HTTP server, fires up the browser helper thread,
             and enters the server main loop.
    """
    if not os.path.exists(DOC_DIR) or not os.path.exists(os.path.join(DOC_DIR, "index.html")):
        print(f"Error: Documentation not found at '{DOC_DIR}'.", file=sys.stderr)
        print("Please build the documentation first by running 'make doc'.", file=sys.stderr)
        sys.exit(1)

    # Change working directory to serve files from DOC_DIR
    os.chdir(DOC_DIR)

    try:
        port = find_free_port()
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    url = f"http://localhost:{port}/index.html"

    # Start browser-open thread so it doesn't block server startup
    browserThread = threading.Thread(target=open_browser_after_delay, args=(url,))
    browserThread.daemon = True
    browserThread.start()

    Handler = http.server.SimpleHTTPRequestHandler
    # Disable default log spam for a cleaner console output
    Handler.log_message = lambda self, format, *args: None

    print("=" * 60)
    print("   KRIBU C++20 DOCUMENTATION SERVER")
    print("=" * 60)
    print(f"  Serving docs at: {url}")
    print("  Press Ctrl+C to stop the server.")
    print("=" * 60)

    # Setup server with port reuse enabled
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("127.0.0.1", port), Handler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[info] Server stopped. Exiting.")
    except Exception as e:
        print(f"\n[error] Server error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
