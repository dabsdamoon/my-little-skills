#!/bin/sh
set -eu

codex_home="${CODEX_HOME:-${HOME}/.codex}"
label="com.dabsdamoon.codex-my-little-skills-upgrade"

usage() {
    printf '%s\n' "Usage: $0 [--codex-home PATH]"
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --codex-home)
            codex_home=$2
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

mkdir -p "$codex_home"
codex_home=$(CDPATH= cd -- "$codex_home" && pwd -P)
platform=$(uname -s)

case "$platform" in
    Darwin)
        plist_path="$HOME/Library/LaunchAgents/$label.plist"
        launchctl bootout "gui/$(id -u)" "$plist_path" >/dev/null 2>&1 || true
        if [ -f "$plist_path" ]; then
            rm -f "$plist_path"
            printf '%s\n' "Removed macOS LaunchAgent: $plist_path"
        fi
        ;;
    Linux)
        unit_dir="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
        timer_name="codex-my-little-skills-upgrade.timer"
        systemctl --user disable --now "$timer_name" >/dev/null 2>&1 || true
        rm -f "$unit_dir/codex-my-little-skills-upgrade.service" "$unit_dir/$timer_name"
        systemctl --user daemon-reload
        printf '%s\n' "Removed Linux systemd user timer: $timer_name"
        ;;
    *)
        printf '%s\n' "Unsupported platform: $platform" >&2
        exit 1
        ;;
esac

installed_script="$codex_home/scripts/update-my-little-skills.sh"
if [ -f "$installed_script" ]; then
    rm -f "$installed_script"
    printf '%s\n' "Removed $installed_script"
fi

printf '%s\n' "Update logs were preserved under $codex_home/log."
