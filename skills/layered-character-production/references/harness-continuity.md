# Harness, references, and recovery

All paths below are relative to the resolved game checkout. Read current files before applying commands; this skill does not ship or replace the game harness.

## Locate the current authority

| Source | What to resolve |
| --- | --- |
| `data/characters/*.tres` and `data/art/animation_profile.json` | Character ID, selected variant, and character-specific visual features |
| `data/art/costume_damage_profile.json` | Character-specific damage design, protected features, expressions, and state requirements |
| `data/art/layer_costume_profile.json` | Shared layer policy, body/garment/bone bindings, and prior-art bundle |
| Current run's `run.json`, `requests/`, `objects/`, manifests, and `records/` | Issued/accepted requests, immutable originals, registration, reviews, and current limitations |
| `docs/art/ADELA-DAMAGE-CONTINUITY-AUDIT.md` | The demonstrated v12 failure and what must be compared after repair |

Do not copy Adela's garment anatomy, damage locations, or bone coordinates onto another character. Resolve that character's bindings first. The v4 Adela reference had incomplete visual approval; its design is a reference baseline, not evidence of a final accepted result.

## Use the existing run protocol

`tools/character_animation.py` plans and records generation work; it does not itself call an image model. From the selected checkout, set `character_run` to the existing run path and inspect it:

```sh
python3 tools/character_animation.py --run "$character_run" status
```

Only when authorized to proceed with generation, request the next job:

```sh
python3 tools/character_animation.py --run "$character_run" next
```

When the checkout's harness supports `expect`, declare before `next` what an edit must keep, change, leave empty or avoid, as canvas regions with a retry reason; the checks become part of the request. `record` then refuses output that fails them or generic hygiene and prints the correction to pass to `reject --reason`; `check` runs the same checks without storing. Passing checks is not design approval.

Use the emitted request's real ID, reference order, and tool arguments. Inspect the referenced images and invoke the available image tool under the current imagegen instructions. Record the returned path promptly through `record`; use `reject` with a concrete defect for failed or unusable output. Recover an already returned PNG after interruption before making a duplicate generation call. Use `retry` when intentionally replacing an accepted source and follow the harness's dependent-frame invalidation.

Before a **new** plan, resolve the character and production mode explicitly. The inspected generic default plans 14 characters; it is unsuitable for a one-character repair. Existing layered authoring scripts may repurpose job slots as part roles, so read their authoring scope and implementation before calling them. Registered job count is not necessarily animation frame count. A script may also target a fixed artifact version; inspect its destinations before rebuilding.

One executor owns a run's generation requests. Do not race another active chat's `next`, registration, or build operations. A known active writer is a reason to coordinate ownership, not to create a competing version silently.

## Bind earlier design before issuing damage requests

For a supported layered costume run, inspect the current CLI and contract before binding:

```sh
python3 tools/layer_costume.py --help
python3 tools/layer_costume.py bind --run "$character_run" --character "$character_id"
```

`character_id` is the selected profile's actual ID. `bind` writes a reference contract and requires pending requests to be settled. Do not call it during diagnosis-only work. The inspected contract pins prior normal, partial, heavy, and HP-expression sources by hash and feeds the applicable references into future requests.

Inspect the emitted request itself: adding references to `run.json` later does not prove an earlier request used them. A previously issued request missing required design sources needs a fresh recorded attempt; keep the original history. A changed profile or source must not inherit stale design approval.

An edit target controls current pose and placement. Earlier full-body damage art controls design features such as lining or attached cloth; it must not overwrite the new rig's camera, scale, or garment-only output format. Keep expression references and facial output separate from garment atlases.

## Keep evidence and derived assets distinct

- Preserve source and returned-image bytes. Record any permitted crop, registration, alpha repair, or mesh transformation as a derived operation.
- Verify dimensions and alpha from the actual output. Prompted dimensions are not observed dimensions.
- Record stable identity, color/material, garment construction, prop side, and view constraints before varying pose or damage.
- Compare raw output **and final composed frames** with the design baseline. A correct returned flap can still disappear under a later mask.
- Preserve current project fields and request provenance. Do not fabricate tool/model IDs or rewrite past requests to make an audit pass.
