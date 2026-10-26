#!/usr/bin/env python3
"""
Start one or more servers, wait for their ports, run a command, then stop the servers.

Each server runs in its own process group with stdout and stderr written to a log
file, so a chatty server cannot fill an unread pipe and stall, and cleanup reaches
every process the server command started (npm -> node -> esbuild, `cd x && ...`).

Usage:
    # Single server
    python3 with_server.py --server "npm run dev" --port 5173 -- python3 automation.py

    # Multiple servers
    python3 with_server.py \
      --server "cd backend && python3 server.py" --port 3000 \
      --server "cd frontend && npm run dev" --port 5173 \
      -- python3 test.py

    # Keep server logs somewhere specific (default: a new temp dir, printed at start)
    python3 with_server.py --log-dir ./server-logs --server "npm run dev" --port 5173 -- python3 test.py
"""

import argparse
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def wait_for_port(port: int, process: subprocess.Popen, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Server exited with code {process.returncode} before port {port} opened")
        try:
            with socket.create_connection(("localhost", port), timeout=1):
                return
        except OSError:
            time.sleep(0.25)
    raise RuntimeError(f"Server did not open port {port} within {timeout}s")


def group_alive(process: subprocess.Popen) -> bool:
    process.poll()  # reap the leader so a zombie does not count as alive
    try:
        os.killpg(process.pid, 0)
    except (ProcessLookupError, PermissionError):
        return False
    return True


def stop_group(process: subprocess.Popen, grace: float = 5.0) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        process.wait()
        return
    deadline = time.monotonic() + grace
    while time.monotonic() < deadline:
        if not group_alive(process):
            return
        time.sleep(0.1)
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait()


def tail(path: Path, lines: int = 20) -> str:
    return "\n".join(path.read_text(errors="replace").splitlines()[-lines:])


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a command with one or more servers running")
    parser.add_argument("--server", action="append", dest="servers", required=True, help="Server shell command (repeatable)")
    parser.add_argument("--port", action="append", dest="ports", type=int, required=True, help="Port for each server, in --server order")
    parser.add_argument("--timeout", type=int, default=30, help="Seconds to wait for each server port (default: 30)")
    parser.add_argument("--log-dir", type=Path, help="Directory for server-N.log files (default: new temp dir)")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run once every server is ready")
    args = parser.parse_args()

    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    if not args.command:
        parser.error("no command given after --")
    if len(args.servers) != len(args.ports):
        parser.error("the number of --server and --port arguments must match")

    log_dir = args.log_dir or Path(tempfile.mkdtemp(prefix="with_server-"))
    log_dir.mkdir(parents=True, exist_ok=True)
    print(f"Server logs: {log_dir}", flush=True)

    # Turn SIGTERM into SystemExit so the finally block still stops the servers.
    signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(128 + signum))

    running: list[subprocess.Popen] = []
    try:
        for i, (cmd, port) in enumerate(zip(args.servers, args.ports), start=1):
            log_path = log_dir / f"server-{i}.log"
            print(f"Starting server {i}/{len(args.servers)}: {cmd}", flush=True)
            with log_path.open("wb") as log:
                # shell=True allows `cd x && ...`; start_new_session puts the shell and
                # everything it spawns in one process group that stop_group() can signal.
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdin=subprocess.DEVNULL,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
            running.append(process)
            try:
                wait_for_port(port, process, args.timeout)
            except RuntimeError as exc:
                print(f"{exc}. Last lines of {log_path}:\n{tail(log_path)}", file=sys.stderr)
                sys.exit(1)
            print(f"Server ready on port {port}", flush=True)

        print(f"Running: {' '.join(args.command)}\n", flush=True)
        sys.exit(subprocess.run(args.command).returncode)
    finally:
        for i, process in enumerate(running, start=1):
            stop_group(process)
            print(f"Server {i} stopped", flush=True)


if __name__ == "__main__":
    main()
