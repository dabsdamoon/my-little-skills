#!/bin/sh
set -eu

marketplace="my-little-skills"
codex_bin="${CODEX_BIN:-}"
codex_home="${CODEX_HOME:-${HOME}/.codex}"
run_now=false
label="com.dabsdamoon.codex-my-little-skills-upgrade"

usage() {
    printf '%s\n' "Usage: $0 [--marketplace NAME] [--codex-bin PATH] [--codex-home PATH] [--run-now]"
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
        --run-now)
            run_now=true
            shift
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

case "$codex_bin" in
    /*) ;;
    *) codex_bin=$(CDPATH= cd -- "$(dirname -- "$codex_bin")" && pwd -P)/$(basename -- "$codex_bin") ;;
esac

mkdir -p "$codex_home"
codex_home=$(CDPATH= cd -- "$codex_home" && pwd -P)

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
source_script="$script_dir/update-codex-marketplace.sh"
if [ ! -f "$source_script" ]; then
    printf '%s\n' "Updater script was not found at $source_script." >&2
    exit 1
fi

platform=$(uname -s)
case "$platform" in
    Darwin)
        if ! command -v launchctl >/dev/null 2>&1; then
            printf '%s\n' "launchctl is required for the macOS adapter." >&2
            exit 1
        fi
        ;;
    Linux)
        if ! command -v systemctl >/dev/null 2>&1; then
            printf '%s\n' "systemctl is required for the Linux adapter. Run the shared updater from your existing scheduler instead." >&2
            exit 1
        fi
        if ! systemctl --user show-environment >/dev/null 2>&1; then
            printf '%s\n' "The systemd user manager is unavailable. Log in as the target user or enable lingering for a headless service account." >&2
            exit 1
        fi
        ;;
    *)
        printf '%s\n' "Unsupported platform: $platform. Run the shared updater from the platform's scheduler." >&2
        exit 1
        ;;
esac

install_dir="$codex_home/scripts"
installed_script="$install_dir/update-my-little-skills.sh"
mkdir -p "$install_dir" "$codex_home/log"
cp "$source_script" "$installed_script"
chmod 700 "$installed_script"

xml_escape() {
    printf '%s' "$1" | sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g' -e 's/"/\&quot;/g' -e "s/'/\\&apos;/g"
}

systemd_escape() {
    printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' -e 's/%/%%/g' -e 's/[$]/$$/g'
}

case "$platform" in
    Darwin)
        launch_agents="$HOME/Library/LaunchAgents"
        plist_path="$launch_agents/$label.plist"
        scheduler_log="$codex_home/log/marketplace-scheduler.log"
        mkdir -p "$launch_agents"

        escaped_script=$(xml_escape "$installed_script")
        escaped_marketplace=$(xml_escape "$marketplace")
        escaped_codex=$(xml_escape "$codex_bin")
        escaped_home=$(xml_escape "$codex_home")
        escaped_log=$(xml_escape "$scheduler_log")

        cat > "$plist_path" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$label</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/sh</string>
    <string>$escaped_script</string>
    <string>--marketplace</string>
    <string>$escaped_marketplace</string>
    <string>--codex-bin</string>
    <string>$escaped_codex</string>
    <string>--codex-home</string>
    <string>$escaped_home</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>StartInterval</key>
  <integer>86400</integer>
  <key>ProcessType</key>
  <string>Background</string>
  <key>StandardOutPath</key>
  <string>$escaped_log</string>
  <key>StandardErrorPath</key>
  <string>$escaped_log</string>
</dict>
</plist>
EOF

        uid=$(id -u)
        launchctl bootout "gui/$uid" "$plist_path" >/dev/null 2>&1 || true
        launchctl bootstrap "gui/$uid" "$plist_path"
        printf '%s\n' "Installed macOS LaunchAgent: $plist_path"
        ;;
    Linux)
        unit_dir="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
        service_name="codex-my-little-skills-upgrade.service"
        timer_name="codex-my-little-skills-upgrade.timer"
        service_path="$unit_dir/$service_name"
        timer_path="$unit_dir/$timer_name"
        mkdir -p "$unit_dir"

        escaped_script=$(systemd_escape "$installed_script")
        escaped_marketplace=$(systemd_escape "$marketplace")
        escaped_codex=$(systemd_escape "$codex_bin")
        escaped_home=$(systemd_escape "$codex_home")

        cat > "$service_path" <<EOF
[Unit]
Description=Refresh the $marketplace Codex marketplace
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/bin/sh "$escaped_script" --marketplace "$escaped_marketplace" --codex-bin "$escaped_codex" --codex-home "$escaped_home"
EOF

        cat > "$timer_path" <<EOF
[Unit]
Description=Refresh the $marketplace Codex marketplace at startup and daily

[Timer]
OnStartupSec=5m
OnCalendar=daily
Persistent=true
RandomizedDelaySec=30m
AccuracySec=1m
Unit=$service_name

[Install]
WantedBy=timers.target
EOF

        systemctl --user daemon-reload
        systemctl --user enable --now "$timer_name"
        printf '%s\n' "Installed Linux systemd user timer: $timer_name"
        ;;
esac

if [ "$run_now" = true ]; then
    /bin/sh "$installed_script" --marketplace "$marketplace" --codex-bin "$codex_bin" --codex-home "$codex_home"
fi

printf '%s\n' "Marketplace: $marketplace"
printf '%s\n' "Codex home: $codex_home"
printf '%s\n' "Schedule: at user startup/login and daily."
