# Review and deliver the actual result

Use the checkout's existing validation and review formats. The purpose of review is to establish what happened in the rendered result, not to accumulate a test count.

## Evidence levels

| Check | Useful evidence | Does not establish |
| --- | --- | --- |
| File and registration | Real dimensions/alpha, hashes, source references, landmarks, links, and public harness validators | Design fidelity or natural motion |
| Composed design | Current output beside its baseline at full size, detail crops, and actual game display size | Browser playback or user aesthetic acceptance |
| Motion and interaction | Observed player state, whole-loop playback, transition frames, and requested controls | Game integration in an untested runtime |
| User acceptance | Explicit feedback tied to the reviewed version | Approval of later changed artwork or contracts |
| Game integration | Supported import plus the repository's native/runtime checks | Acceptance inferred from a standalone demo |

For damage work, compare normal/partial/heavy at the same body scale, camera, and gait phase. Check the existing design's silhouette, material/lining/attached cloth, neckline, actual face binding, protected features, exposed-region continuity, and arm/garment depth order. Do not normalize each state's visible bounds separately; that conceals scale drift.

For motion, inspect the whole loop at normal speed and the defective interval slowly or frame by frame. Review foot contact, joint seams, volume, occlusion switches, secondary motion, and the final-to-first transition. Use enlarged details and the current target game size (historically 72px high for the legacy front sprites); use the actual current renderer size when it differs.

## Use current harness checks truthfully

Run the narrowest applicable public validation entrypoints and the repository-mandated checks for the changed scope. Follow its test skill when changing automated tests. Do not claim headless tests validate native input or a playable page.

In the inspected costume harness, this command writes a conformance report:

```sh
python3 tools/layer_costume.py audit --run "$character_run" --character "$character_id"
```

An exit code of zero means the report was written. Read `design_status`, issues, and incomplete review checks in `records/design-conformance.json`. A technical pass can coexist with `needs_redraw` or `needs_art_review`.

`records/design-review.json` is meaningful only for the model and profile hashes actually reviewed. Record observed checks through the project's existing format, with frame/state and evidence references. Leave unavailable checks unverified. Never synthesize pass flags to satisfy the audit, reuse an older hash's approval, or equate the agent's visual inspection with user acceptance.

## Make the artifact reviewable

Build the final review entry, usually the current run's `review/index.html`, with its real manifest and assets. The filename is a convention, not proof that data is present. A file under `tools/templates/` may be a source template; do not hand it off as the completed artifact.

Reuse the existing player. For requested motion review, provide working play/pause, speed, frame stepping or scrubbing, and enough background/zoom controls to expose seams. For costume or HP work, include the applicable layer and state controls. Avoid adding irrelevant controls for unimplemented capabilities.

Use the available browser skill before inspecting the page in a browser. Confirm rendered character frames, a complete loop, and the requested controls in the actual page. Retain observed state/frame evidence where useful; a single still, an elapsed wait, or HTTP success does not verify continuous motion. If browser access is blocked, report the exact limitation, preserve the built artifact and supporting frame comparisons, and leave playback/interaction unverified. Do not bypass a denied access path.

Use the supported app opening tool when available and return an absolute link to the built entry. A queued open request is not proof that the page is displayed. Keep generated assets alongside the artifact with resolvable relative paths.

## Handoff and game installation

Report the built artifact, editable parts/rig sources, relevant checks actually performed, and remaining visual or runtime limits. Clearly distinguish a comparison page, static pose sheet, motion preview, completed harness export, and installed game asset.

Generic `deliver` is appropriate only when the current run's real production mode satisfies its exporter. Do not pass a part-atlas run or a 48-frame layered study off as a seven-image runtime bundle. Inspect supported import formats before game installation and apply only within the user's requested scope; finish independent production work while unresolved feedback remains recorded.
