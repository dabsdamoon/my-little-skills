A. Survival HUD — daylight field kit

Use a sunlit, desaturated moss battlefield with warm ivory instruments, charcoal type and hard-edged geometry. Reserve vermilion for danger and lost health; cobalt identifies the controlled character. No introduction label or headline: open directly into play.

The composition follows what the player is doing. A broad active-character health rail anchors the lower left. Two smaller reserve tabs climb the right edge, each showing a portrait, name, individual HP and swap key. They read as available reinforcements, not three competing cards.

Compact desktop wireframe:

+-----------------------------------------------------+
| XP 340 / 500 ====================                    |
|                                                     |
|                   ↑ danger                          |
|                                                     |
|                    PLAYER                 [2 MIRA    ]|
|                                           [HP 62/80 ]|
|                                           [READY    ]|
|                                                     |
|                                           [3 ADELA  ]|
|                                           [HP 41/70 ]|
|                                           [READY    ]|
|                                                     |
| [1 ACTIVE: NAE] HP 78/100 ========    REMAINING 04:32 |
+-----------------------------------------------------+

Swap behavior:
- Press 1, 2 or 3 to control that character. The active character’s key is visibly selected. Attacks remain automatic; omit an attack control.
- After any swap, both reserve tabs show the same draining 1.25-second cooldown strip and remaining tenths. Replace READY with “Swap in 1.2s.” Keep HP legible throughout. Restore READY simultaneously when the shared cooldown ends.
- Exchange active and reserve presentations immediately on a successful swap. Retain each character’s portrait and accent pattern so positions can change without losing identity.

Nearby danger uses short directional wedges around the player. Wedges become thicker and more densely hatched as threats approach. Edge indicators summarize threats outside the viewport. Never rely on red alone or cover the player’s feet with warnings.

Landscape touch adaptation: move the reserve tabs to the lower right as two 64-pixel swap targets, with health and readiness inside. Add a movement stick at lower left; lift the active health rail above its reach. Move the countdown above the swap targets. Respect device safe areas.

Build brief: ship one HUD scene using flat panels, existing portraits, bars and directional wedges. Use tabular timer digits and minimum 16-pixel text. Keep the central combat area clear. Check readable individual HP, synchronized cooldown feedback, threat direction and comfortable touch reach during movement. This is the selected implementation direction; proceed without another approval meeting.

B. Search-button hit area

Keep the button’s visible height at 36 pixels. Expand its interactive bounds four pixels above and below, producing a 44-pixel-high target; expand width only if it is below 44 pixels. Use a transparent hit region without changing layout dimensions.

Verify unchanged rendering and surrounding positions, successful clicks/taps throughout the added bounds, unchanged keyboard activation, and no overlap with neighboring controls or clipping by ancestors.
