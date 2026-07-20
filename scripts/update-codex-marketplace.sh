#!/bin/sh
set -eu

marketplace="my-little-skills"
codex_bin="${CODEX_BIN:-}"
codex_home="${CODEX_HOME:-${HOME}/.codex}"
log_path=""

usage() {
    printf '%s\n' "Usage: $0 [--marketplace NAME] [--codex-bin PATH] [--codex-home PATH] [--log-path PATH]"
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --marketplace)
            marketplace=$2
            shift 2
            ;;
        --codex-bin)
            codex_bin=$2
            shift 2
            ;;
        --codex-home)
            codex_home=$2
            shift 2
            ;;
        --log-path)
            log_path=$2
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            printf '%s\n' "Unknown argument: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

case "$marketplace" in
    ""|*[!A-Za-z0-9._-]*)
        printf '%s\n' "Invalid marketplace name: $marketplace" >&2
        exit 2
        ;;
esac

if [ -z "$codex_bin" ]; then
    codex_bin=$(command -v codex 2>/dev/null || true)
fi
if [ -z "$codex_bin" ] || [ ! -f "$codex_bin" ]; then
    printf '%s\n' "Codex CLI was not found. Install Codex and pass --codex-bin if it is not on PATH." >&2
    exit 1
fi

mkdir -p "$codex_home"
codex_home=$(CDPATH= cd -- "$codex_home" && pwd -P)
export CODEX_HOME="$codex_home"

if [ -z "$log_path" ]; then
    log_path="$codex_home/log/marketplace-updates.log"
fi
mkdir -p "$(dirname -- "$log_path")" "$codex_home/.locks"

if [ -f "$log_path" ]; then
    log_size=$(wc -c < "$log_path" | tr -d ' ')
    if [ "$log_size" -gt 1048576 ]; then
        mv -f "$log_path" "$log_path.1"
    fi
fi

lock_dir="$codex_home/.locks/marketplace-$marketplace"
if ! mkdir "$lock_dir" 2>/dev/null; then
    existing_pid=""
    if [ -f "$lock_dir/pid" ]; then
        existing_pid=$(cat "$lock_dir/pid" 2>/dev/null || true)
    fi
    case "$existing_pid" in
        ""|*[!0-9]*) ;;
        *)
            if kill -0 "$existing_pid" 2>/dev/null; then
                printf '%s\n' "Marketplace updater '$marketplace' is already running."
                exit 0
            fi
            ;;
    esac
    rm -f "$lock_dir/pid"
    rmdir "$lock_dir" 2>/dev/null || {
        printf '%s\n' "Could not clear stale updater lock: $lock_dir" >&2
        exit 1
    }
    mkdir "$lock_dir"
fi

printf '%s\n' "$$" > "$lock_dir/pid"
cleanup() {
    rm -f "$lock_dir/pid"
    rmdir "$lock_dir" 2>/dev/null || true
}
trap cleanup EXIT HUP INT TERM

started_at=$(date '+%Y-%m-%d %H:%M:%S')
printf '[%s] marketplace=%s codex_home=%s status=starting\n' "$started_at" "$marketplace" "$codex_home" >> "$log_path"

if "$codex_bin" plugin marketplace upgrade "$marketplace" >> "$log_path" 2>&1; then
    exit_code=0
    status=succeeded
else
    exit_code=$?
    status=failed
fi

finished_at=$(date '+%Y-%m-%d %H:%M:%S')
printf '[%s] marketplace=%s status=%s exit=%s\n' "$finished_at" "$marketplace" "$status" "$exit_code" >> "$log_path"

if [ "$exit_code" -ne 0 ]; then
    printf '%s\n' "Codex marketplace update failed with exit code $exit_code. See $log_path." >&2
    exit "$exit_code"
fi

printf '%s\n' "Updated Codex marketplace '$marketplace' in '$codex_home'. Log: $log_path"
