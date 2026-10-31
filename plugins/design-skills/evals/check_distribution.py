#!/usr/bin/env python3
"""Check the published frontend-design mirror and plugin metadata, not prose."""

import argparse
import json
from pathlib import Path


def check(root: Path) -> list[str]:
    source = root / "skills/frontend-design"
    plugin = root / "plugins/design-skills"
    mirror = plugin / "skills/frontend-design"
    errors = []
    if not source.is_dir() or not mirror.is_dir():
        return ["canonical or published frontend-design directory is missing"]

    def files(folder: Path) -> dict[str, bytes]:
        return {
            str(path.relative_to(folder)): path.read_bytes()
            for path in folder.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }

    expected, published = files(source), files(mirror)
    for name in sorted(expected.keys() | published.keys()):
        if expected.get(name) != published.get(name):
            errors.append(f"distribution differs: {name}")

    manifests = []
    for folder in [".claude-plugin", ".codex-plugin"]:
        try:
            manifests.append(json.loads((plugin / folder / "plugin.json").read_text()))
        except (OSError, ValueError) as error:
            errors.append(f"invalid {folder}/plugin.json: {error}")
    if len(manifests) == 2:
        for key in ["name", "version", "description", "author"]:
            if key not in manifests[0] or manifests[0][key] != manifests[1].get(key):
                errors.append(f"plugin metadata differs: {key}")
        if manifests[0].get("name") != "design-skills":
            errors.append("plugin name does not match design-skills")
        declared = manifests[1].get("skills")
        if not isinstance(declared, str) or (plugin / declared).resolve() != mirror.parent.resolve():
            errors.append("Codex manifest does not expose the plugin skills directory")
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    args = parser.parse_args()
    problems = check(args.root)
    for problem in problems:
        print(problem)
    if not problems:
        print("frontend-design distribution and plugin metadata match")
    raise SystemExit(bool(problems))
