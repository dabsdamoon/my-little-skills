A. Survival-action HUD

Choose “rescue instrument panel”: warm ivory instrumentation around an unobstructed arena, ink-black numerals, signal-orange danger marks and cobalt selection. No introductory heading or decorative copy. This gives the game the urgency of equipment used in the field.

A second direction, a theatrical neon spotlight with an oversized active portrait, offers stronger character drama but competes with enemy silhouettes. Build the instrument panel now; it requires only type, flat shapes and existing portraits.

Compact landscape wireframe:

[ LV 06 ================= XP 72% ]

         PLAYFIELD
  directional danger marks at edges

[ACTIVE: MIRA]             [2 ADELA  HP 48/80]
[HP 63/100]    03:42 LEFT   [3 NARI   HP 90/90]

The active character gets a compact rectangular identification strip at lower left. Standby characters become two stacked, individually tappable tabs at lower right, each with a portrait, name, keyboard number and its own HP bar and values. Their unequal relationship replaces the three-card composition. HP bars retain the same scale within each character’s maximum; never combine team health.

Timer sits low in the central instrument strip, using large tabular numerals. Experience is a thin top-edge track with level and percentage. Keep these anchored during swaps so the battlefield never shifts.

Ready standby tabs show a small check and “READY.” After any successful swap, both tabs show the same 1.25-second countdown and a draining outline. Keep HP legible underneath; do not grey out the whole tab. A defeated teammate reads “DOWN” and cannot be selected. Selection changes the cobalt border and active identification immediately.

Nearby danger uses short orange edge wedges pointing toward threats outside the view and a clear ground marker for immediate hazards. Wedge shape and direction carry meaning without relying on color. Restrict indicators to information the player is entitled to observe.

Build brief: Barlow Condensed for character names; Source Sans 3 for health and controls. Use opaque ivory text backplates, 2-pixel ink rules and generous numeral spacing. Reserve orange for danger. Animate only successful swaps with a 120ms border sweep; respect reduced motion. Attacks remain automatic. Desktop: WASD/arrows move; 1–3 select characters. Landscape touch: reserve the lower-left thumb zone for movement and use at least 56-pixel-high standby tabs above safe-area insets. Keep the active health strip above the movement zone. Verify a swap during heavy combat, low HP, simultaneous cooldown and landscape thumb reach.

B. Search-button hit area

Keep the visible 36-pixel button and its layout box unchanged. Extend its interactive surface 4 pixels above and below using a transparent, absolutely positioned pseudo-element belonging to the existing button. Preserve its accessible name, focus behavior and click handler.

Verify the resulting target measures at least 44 pixels high, both added bands activate the button, surrounding elements retain their positions, and screenshots remain visually identical. Check ancestor clipping and neighboring targets so the extension stays reachable without intercepting another control.
