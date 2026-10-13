# Rig and costume mechanics

Use the current `CHARACTER-LAYER-AUTHORING.md` and character bindings as authority. The inspected implementation uses PNG parts, articulated mesh transforms, generated cloth keys, and frame-by-frame composition. Spine or Live2D is not a dependency of this workflow.

## Registration and parts

- Preserve the character's canonical body canvas, scale, ground, shoulder/waist/foot landmarks, and view. The inspected Adela setup uses 1024×1536; verify the current profile before applying it elsewhere.
- Register newly generated parts using named tailoring/anatomical landmarks. Store source and target coordinates, units, transform, and anatomical versus screen-left/right conventions. New art requires inspected correspondence, not blind reuse of an old atlas crop or bounding box.
- Keep covered body, torso garments, sleeves, lower garment, accessories, and independently moving limb segments separate. Complete hidden connections; retain enough overlap for the requested range of motion.
- Use rigid parts where appropriate, local mesh deformation where bending needs continuity, and replacement drawings for expression or substantial view changes. Whole-body warping must not substitute for independent limb movement.
- Preserve facial/body volume while moving cloth. Inspect shoulder, elbow, wrist, hip, knee, and ankle extremes relevant to the requested action.

## Occlusion and motion

Store pose-dependent draw order independently of bone parenting. Change depth only for the segment that actually crosses another layer, usually the forearm and hand, and keep the source art's overlaps everywhere else. If the source paints a garment armhole over the sleeve, the shoulder sleeve and upper arm stay under it in every frame, even while the forearm swings in front. Switching a whole limb with its sleeve exposes the sleeve's cut inner edge and makes the arm jump forward for one frame.

When a garment piece must follow a moving segment, such as a cuff over the forearm, split it with complementary masks from the same posed pixels at a row where the two halves provably never meet the other layers involved, and give that piece the segment's depth. Choose switch frames where the swapped parts barely overlap, and measure the counterfactual: drawing a switch frame in the other order should change almost no pixels. A correct hand alone does not prove the whole arm is correct; inspect the frames on both sides of each switch at full size.

Review rear/side/front keys before generating all inbetweens. For walking, inspect planted feet, root travel, limb bend direction, and contact/passing/up/down poses. Reuse the run's actual timing; the legacy seven-image export and the layered 48-frame demo are different formats. Do not impose either one's frame count, cadence, or origin on the other.

Keep frame evaluation deterministic and compare both position and motion continuity at the loop boundary. Check draw-order switches at their surrounding frames. Add cloth, hair, or accessory follow-through only after the primary contacts and silhouettes work.

## Damage is a new garment shape

Preserving body scale does not require damaged cloth to fit inside the intact garment silhouette. An attached flap may sag outside it. Do not intersect all damaged alpha with intact alpha, or force heavy damage to be a pixelwise subset of partial damage. Inspect protected masks along actual seams/material boundaries so they do not erase desired lining, tears, or neckline changes.

Read each character's damage signature and protected regions. For the inspected Adela contract, the required details include ivory sleeve lining/frayed cuff, an attached lowered jacket flap, the specified blouse neckline change, and separate HP face variants. Her protected waist/skirt and covered foundation are character-specific; do not generalize them to the roster.

Give attached cloth a defined attachment and motion responsibility. It may need a separate part and local follow-through instead of being flattened into a static garment alpha. Preserve the authored tear, overlap, edge thickness, and lining when composing and deforming it.

## Separate costume, expression, and hit reaction

The inspected project uses partial/heavy thresholds at HP 70%/35%; read current game/profile rules before implementing. Costume damage persists after healing until the relevant reset, while the face follows current HP. Bind actual expression artwork, not just a state label.

Review a sequence that enters partial/heavy damage, heals, and starts a new mission. Inspect the expected outfit and face in the same rendered state. A button that decreases HP is not a hit-reaction animation. If a hit response is requested, define its anticipation/contact/recoil/settling and transition back to the existing motion separately.

Garment-off review is useful for finding baked-in clothing, missing body connections, and stale occlusion masks. When damage exposes a previously covered region, use a state-appropriate body mask; the intact garment's mask can hide valid underlying artwork.
