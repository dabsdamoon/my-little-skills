A. Build brief: a daylight field instrument

Use a warm ivory, ink-black HUD with vermilion reserved for threats. The battlefield remains the dominant surface. Replace the heading and card row with an asymmetric instrument strip anchored to the bottom corners: a compact team roster on the left, a large remaining-time readout on the right, and a thin experience measure connecting them. No introductory copy.

Use Barlow Condensed for large numerals and Atkinson Hyperlegible for names and small labels. Flat, sharply outlined surfaces and precise tick marks give the interface character without bespoke artwork or decorative animation.

Landscape sketch:

+--------------------------------------------------+
|       directional danger marks at field edges    |
|                                                  |
|                  PLAY AREA                       |
|                                                  |
| > 1 MIRA   HP 68/90 =================             |
|   2 ADELA  HP 42/75 =========        REMAINING     |
|   3 NERI   HP 81/81 ==============      02:16      |
|   SWAP IN 0.8s                                    |
| LEVEL 7  [========== experience =====----]  72/100 |
+--------------------------------------------------+

The active character gets an extended ink baseline and solid arrow; standby teammates are indented. Every character retains a labeled HP bar and numeric value. Names here are placeholders for production character data. Avoid portraits in the first build.

Press 1–3 to select a character. Selecting the active character does nothing. While the shared 1.25-second cooldown runs, both standby actions show the same lock mark; one labeled countdown beneath the roster explains the shared restriction. When it ends, replace the countdown with “SWAP READY,” remove both locks, and make eligible teammates actionable. Empty HP reads “DOWN,” never “READY.” Do not imply that attacks need input.

Give each roster row a 56-pixel-high touch target; anchor the roster within the left thumb’s reach in landscape. Keep the right side available for movement controls when touch input is implemented. Desktop movement bindings remain visible in the controls help, outside combat.

Nearby danger uses short edge wedges pointing toward approaching threats, with stronger thickness as danger increases. Preserve visible enemies and projectiles. Threat markings use shape as well as color; never encode HP or readiness through color alone.

Build one HUD scene with shared cooldown state, reusable roster rows, and a connecting XP strip. Verify with full/low/zero HP, both cooldown endpoints, long names, and the smallest supported landscape viewport. Keep timer and HP readable over bright and dark terrain. This direction is ready to build.

B. Search button only

Keep the button’s visible 36-pixel box and existing layout dimensions. Expand its interactive bounds vertically by 4 pixels above and below using an absolutely positioned transparent hit-area pseudo-element attached to the existing button. Preserve its current width if already at least 44 pixels; otherwise expand the hit area horizontally too. No wrapper spacing changes.

Verify clicks across the expanded bounds activate search, neighboring controls remain reachable, keyboard behavior and focus indication persist, and before/after screenshots show identical visible placement. Check ancestor clipping and stacking so the added area actually receives input.
