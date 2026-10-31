A. Direction: a field-kit HUD

Make the fight the composition. Use an asymmetric instrument strip along the left edge, with a large active-character silhouette above two compact reserve tabs. The scene stays bright and readable: dusty sage terrain, bone-colored instruments, charcoal numerals and vermilion danger marks. No heading, introductory label or three-card roster.

Landscape sketch:

[ACTIVE portrait / HP]                         [pause]
[reserve A / HP / 2]       COMBAT FIELD
[reserve B / HP / 3]       player + danger arcs

[XP ================= level 7]      [remaining 04:32]

The active portrait is 72 pixels tall; its HP is a thick vertical gauge with a numeric value. Each reserve tab is 56 pixels tall, with portrait, individual HP bar and keyboard assignment. The difference in scale makes the current fighter obvious. Portraits exchange positions after a successful swap; keyboard assignments remain attached to characters, so movement never changes a learned shortcut.

Both reserve tabs share a single visible cooldown rail beside them. On swap, it drains over 1.25 seconds; both tabs show the same remaining tenths and lose their readiness outline. At zero, both regain the outline and a small “Ready” label. An unavailable teammate instead says why, such as “Down.” Color reinforces these states; shape and text carry them.

Keep danger in the world: short directional wedges outside the player’s silhouette point toward nearby threats, becoming thicker as danger closes. Offscreen threats get matching edge ticks. Avoid a full-screen red wash that obscures movement. Automatic attacks require no attack control.

Build brief: implement this one direction using existing portraits, flat shapes and text. Anchor the XP strip and countdown above screen-safe margins; give the countdown tabular digits and a clock icon. Reserve clear space around the player. On desktop, show WASD movement and character shortcuts once, then fade the movement hint. For landscape touch, move the two reserve tabs to the right thumb zone, retain the active gauge at upper left and add a floating movement pad on the left. Keep touch targets at least 56 pixels. Verify cooldown synchronization, low HP readability, danger visibility and thumb clearance in one playable encounter. Proceed without another approval meeting.

B. Button hit area only

Keep the visible 36-pixel button and its layout box unchanged. Extend its clickable region with a transparent, absolutely positioned button pseudo-element, four pixels above and below. Ensure the resulting width is also at least 44 pixels without changing visible styling.

Verify clicks in the added region activate the existing action, surrounding elements retain their coordinates, keyboard behavior and focus styling remain unchanged, and no clipping or adjacent target overlap intercepts the expanded hit area.
