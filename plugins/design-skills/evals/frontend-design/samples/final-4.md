A. Survival HUD

Required: individual HP for all three characters; one active character; direct access to both waiting teammates; a shared 1.25-second swap cooldown; remaining time, XP, nearby danger and teammate readiness. Attacks remain automatic. The old composition and wording are provisional.

Two compact alternatives:

1. Distributed combat HUD
Attention starts at the moving character: a compact HP bar follows them, while directional danger marks sit around the combat focus. A small time readout sits upper left; XP runs along the bottom edge. Two unequal-to-the-active, fixed swap controls sit lower right, each showing its teammate’s portrait, HP and readiness. Keyboard players move with WASD and select a waiting teammate with Q/E; landscape touch uses a left movement pad and the same two right-thumb controls. All combat information stays visible. Tradeoff: character-following HP needs careful placement to avoid obscuring enemies.

2. Command strip
Reserve a shallow bottom band: active character and HP at left, time and XP in the middle, two waiting teammates and the shared cooldown at right. Danger remains directional within the playfield. Movement and swap inputs match option 1. This groups resource checks and teammate selection into one predictable scan. Tradeoff: the strip consumes vertical combat space, especially on landscape phones.

Recommendation: option 1. Unlike the previous timer-over-three-equal-cards sketch, it places current survival information beside the character and makes the waiting teammates actionable controls. Unlike the command strip, it separates immediate danger from peripheral resource checks, preserving more battlefield height.

Build brief for the next designer:
- Implement the distributed layout as the recommended direction under the existing authorization. Positions are implementation choices, not new requirements. Omit introductory headings and slogans.
- Give each swap control a minimum 56-pixel touch target. Display a single shared countdown spanning both controls; both become unavailable together after a swap. Show “Ready” when available, using text and shape alongside color. Keep each HP value distinct and continuously visible.
- Use plain time text, such as “03:42 remaining,” and a labeled XP track. Assume the game supplies danger direction/proximity; preserve its detection rules. Keep warnings legible over varied terrain with restrained backing and outlines.
- Keep critical controls inside landscape safe areas. Validate low HP, unequal teammate HP, cooldown expiry, dense enemies and touch reach in motion. No rendering or playtesting has been performed. No further layout decision is needed before a first build.

B. Search button

Preserve the 36-pixel visible button and its layout footprint. Extend its clickable element with a transparent, absolutely positioned hit region four pixels above and below, producing a 44-pixel target without changing document flow. Preserve existing labels, focus styling and activation behavior.

Verify the added strips activate search, surrounding elements retain their positions, neighboring targets do not overlap, and keyboard focus/Enter/Space behavior remains unchanged. Compare before/after screenshots for identical visible styling. These are verification requirements, not completed checks.
