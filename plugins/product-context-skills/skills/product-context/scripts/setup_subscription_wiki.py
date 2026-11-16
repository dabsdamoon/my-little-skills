#!/usr/bin/env python3
"""Explicitly install the subscription-only MCP runtime for local coding hosts."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile

SKILL = Path(__file__).resolve().parents[1]
VERSION = json.loads((SKILL / 'runtime/package.json').read_text())['version']
NAME = 'product_context'


class SetupError(Exception):
    pass


def safe_destination(path: Path) -> None:
    for item in [*reversed(path.parents), path]:
        if item.is_symlink():
            raise SetupError(f'UNSAFE_DESTINATION: Use a canonical path without symlinked ancestors: {item}')
        if item != path and item.exists() and not item.is_dir():
            raise SetupError('UNSAFE_DESTINATION: An install ancestor is not a directory.')


def write_json(path: Path, value: dict) -> None:
    safe_destination(path)
    descriptor, name = tempfile.mkstemp(prefix=f'.{path.name}-', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'w') as stream:
            stream.write(json.dumps(value, indent=2) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


@contextmanager
def setup_lock(parent: Path):
    # Kernel ownership is released on process exit, so an interrupted install can
    # be retried without confusing an active npm transaction with an abandoned one.
    import fcntl
    file = parent / '.setup.lock'
    safe_destination(file)
    parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(file, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise SetupError('UNSAFE_DESTINATION: The setup lock must be a regular file.')
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SetupError('SETUP_BUSY: Another installer owns this runtime and registration transaction.') from None
        yield
    finally:
        os.close(descriptor)


def command(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def required(args: list[str], cwd: Path | None = None) -> str:
    result = command(args, cwd)
    if result.returncode:
        raise SetupError(f'COMMAND_FAILED: {args[0]} {args[1]} failed; no API fallback was attempted.')
    return result.stdout


def files() -> dict[str, str]:
    result = {}
    for directory, names, filenames in os.walk(SKILL):
        names[:] = [name for name in names if name not in {'node_modules', '__pycache__', '.git'}]
        for name in filenames:
            if name.endswith('.pyc') or name in {'.installed.json', '.installing.json'}:
                continue
            source = Path(directory) / name
            if source.is_symlink():
                raise SetupError('UNSAFE_SOURCE: Refusing symlinked skill files.')
            result[str(source.relative_to(SKILL))] = hashlib.sha256(source.read_bytes()).hexdigest()
    return result


def registration(host: str, server: Path) -> list[str]:
    env = ['--env', 'OPENWIKI_TELEMETRY_DISABLED=1', '--env', 'DO_NOT_TRACK=1'] if host == 'codex' else ['-e', 'OPENWIKI_TELEMETRY_DISABLED=1', '-e', 'DO_NOT_TRACK=1']
    scope = [] if host == 'codex' else ['--scope', 'user', '--transport', 'stdio']
    return [host, 'mcp', 'add', NAME, *scope, *env, '--', 'node', str(server), '--host', host]


def inspect_registration(host: str, owned: dict, expected: Path) -> bool:
    result = command([host, 'mcp', 'get', NAME, *(['--json'] if host == 'codex' else [])])
    if result.returncode:
        return False
    previous = owned.get(host)
    text = result.stdout
    try:
        value = json.loads(text)
        transport = value.get('transport', value)
        args = transport.get('args', [])
        reported = args[0] if transport.get('command') == 'node' and args else None
    except json.JSONDecodeError:
        reported = previous if previous and previous in text and 'Command: node' in text else None
    if not reported or reported not in {previous, str(expected)}:
        raise SetupError(f'UNMANAGED_SERVER: Existing {host} MCP server {NAME} was left unchanged.')
    if previous is None and reported != str(expected):
        raise SetupError(f'UNMANAGED_SERVER: Existing {host} server has no installation record.')
    return reported == str(expected)


def install_runtime(target: Path, manifest: dict[str, str]) -> None:
    safe_destination(target)
    for name in ['.installed.json', '.installing.json']:
        safe_destination(target / name)
    expected = {'owner': NAME, 'version': VERSION, 'files': manifest}
    if target.exists():
        receipt = next((target / name for name in ['.installed.json', '.installing.json'] if (target / name).exists()), None)
        if receipt is None or json.loads(receipt.read_text()) != expected:
            raise SetupError('VERSION_CONFLICT: The target is not this exact managed version; use a new version/path.')
        for relative, digest in manifest.items():
            installed = target / relative
            safe_destination(installed)
            if installed.is_symlink() or hashlib.sha256(installed.read_bytes()).hexdigest() != digest:
                raise SetupError('VERSION_CONFLICT: Installed managed files changed; no files were overwritten.')
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = Path(tempfile.mkdtemp(prefix='.product-context-install-', dir=target.parent))
        try:
            for relative in manifest:
                destination = temporary / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(SKILL / relative, destination)
            write_json(temporary / '.installing.json', expected)
            temporary.rename(target)
        finally:
            if temporary.exists():
                shutil.rmtree(temporary)
    if not (target / '.installed.json').exists():
        required(['npm', 'ci', '--ignore-scripts', '--no-audit', '--no-fund'], target / 'runtime')
        required(['node', str(target / 'runtime/server.mjs'), '--host', 'codex', '--self-check'])
        write_json(target / '.installed.json', expected)
        (target / '.installing.json').unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', choices=['claude', 'codex', 'both'], default='both')
    parser.add_argument('--install-root', type=Path, default=Path.home() / '.local/share/product-context' / VERSION)
    parser.add_argument('--install', action='store_true', help='Explicitly install dependencies and register user MCP servers.')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    hosts = ['claude', 'codex'] if args.host == 'both' else [args.host]
    target = args.install_root.expanduser().absolute()
    server = target / 'runtime/server.mjs'
    report = {'mode': 'install' if args.install else 'plan', 'version': VERSION, 'hosts': hosts,
              'runtime': str(target), 'commands': [registration(host, server) for host in hosts],
              'model_calls': 0, 'api_fallback': False, 'schedules_installed': False}
    if args.install:
        for executable in ['node', 'npm', 'python3', *hosts]:
            if not shutil.which(executable):
                raise SetupError(f'MISSING_TOOL: Install {executable} before running setup.')
        version = required(['node', '--version']).strip().removeprefix('v').split('.')
        if tuple(map(int, version[:2])) < (22, 22):
            raise SetupError('NODE_VERSION: Node.js 22.22 or newer is required.')
        registry = target.parent / 'registrations.json'
        safe_destination(target)
        safe_destination(registry)
        with setup_lock(target.parent):
            owned = json.loads(registry.read_text()) if registry.exists() else {}
            ready = {host: inspect_registration(host, owned, server) for host in hosts}
            install_runtime(target, files())
            for host in hosts:
                required(['node', str(server), '--host', host, '--check-auth'])
            for host in hosts:
                if ready[host]:
                    continue
                previous = owned.get(host)
                if previous:
                    required([host, 'mcp', 'remove', NAME, *(['--scope', 'user'] if host == 'claude' else [])])
                try:
                    required(registration(host, server))
                except SetupError:
                    if previous:
                        required(registration(host, Path(previous)))
                    raise
                owned[host] = str(server)
                write_json(registry, owned)
        report['registered'] = hosts
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (SetupError, OSError, ValueError) as error:
        print(json.dumps({'error': str(error)}))
        raise SystemExit(2)
