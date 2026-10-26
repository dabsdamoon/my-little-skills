"""Tests for scripts/with_server.py. Loopback only; no internet, no Playwright.

    pytest plugins/developer-workflow-skills/skills/webapp-testing/tests
    python3 plugins/developer-workflow-skills/skills/webapp-testing/tests/test_with_server.py
"""

import os
import shlex
import socket
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "with_server.py"
PY = shlex.quote(sys.executable)


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def port_open(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1):
            return True
    except OSError:
        return False


def group_gone(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return True
    return False


def run_with_server(server_cmd: str, port: int, log_dir: Path, *command: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--log-dir", str(log_dir), "--timeout", "10",
         "--server", server_cmd, "--port", str(port), "--", *command],
        capture_output=True, text=True, timeout=60,
    )


def test_stops_every_process_in_the_server_group(tmp_path: Path) -> None:
    port = free_port()
    pgid_file = tmp_path / "pgid"
    # `& wait` makes http.server a child of the shell, as `npm run dev` makes node a child.
    server = (
        f"echo $$ > {shlex.quote(str(pgid_file))}; "
        f"{PY} -m http.server {port} --bind 127.0.0.1 & wait"
    )
    fetch = f"import urllib.request; urllib.request.urlopen('http://127.0.0.1:{port}/', timeout=5)"

    result = run_with_server(server, port, tmp_path / "logs", sys.executable, "-c", fetch)

    assert result.returncode == 0, result.stdout + result.stderr
    pgid = int(pgid_file.read_text())
    assert group_gone(pgid), f"process group {pgid} still alive"
    assert not port_open(port)
    assert "GET / HTTP" in (tmp_path / "logs" / "server-1.log").read_text()


def test_server_that_writes_more_than_a_pipe_buffer_still_starts(tmp_path: Path) -> None:
    port = free_port()
    noisy = f"{PY} -c \"import sys; sys.stderr.write('x' * 1_000_000)\""
    server = f"{noisy}; exec {PY} -m http.server {port} --bind 127.0.0.1"

    result = run_with_server(server, port, tmp_path / "logs", sys.executable, "-c", "pass")

    assert result.returncode == 0, result.stdout + result.stderr
    assert not port_open(port)


def test_reports_a_server_that_exits_early(tmp_path: Path) -> None:
    port = free_port()

    result = run_with_server("echo boom >&2; exit 3", port, tmp_path / "logs", sys.executable, "-c", "pass")

    assert result.returncode == 1
    assert "exited with code 3" in result.stderr
    assert "boom" in result.stderr


if __name__ == "__main__":
    tests = [obj for name, obj in sorted(globals().items()) if name.startswith("test_") and callable(obj)]
    for test in tests:
        with tempfile.TemporaryDirectory() as tmp:
            test(Path(tmp))
        print(f"PASS {test.__name__}")
    print(f"{len(tests)} passed (plain-script runner; pytest not used)")
