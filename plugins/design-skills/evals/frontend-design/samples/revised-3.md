A. Survival-action HUD

Requirements: movement; three individual HP values; two available swap targets; one shared 1.25-second swap cooldown; automatic attacks; remaining time, XP, nearby danger; keyboard and landscape touch support. The previous placement and promotional copy remain provisional.

Two structural directions:

1. Split cockpit. Keep the arena dominant. Time and XP occupy a compact upper-left instrument; active HP sits above the lower-left movement area. Two standby controls stack at the right thumb. Nearby threats register at the corresponding arena edge. Attention starts with the character and danger; swapping follows a short glance toward the right. All information stays visible, but the widely separated instruments require more eye travel on large monitors.

2. Run strip. Consolidate time, XP and all three HP readings into one shallow bottom strip. Enlarge the active character's segment; attach two smaller swap buttons to its right. Movement stays above the strip on the left, with danger indicators at arena edges. Attention travels along one horizontal baseline, making squad comparison easier. The strip consumes continuous vertical space, particularly costly on landscape phones.

Recommendation: split cockpit. It preserves the movement field and gives touch input a clear left/right division. Its separate status and action zones differ structurally from the run strip's single comparison surface. Proceed with this recommendation under the existing authorization.

Build brief:

  [04:18 left] [XP =====---]
  > danger         ARENA         danger <
  [Active: Mira  HP 72/100]      [2 Adela 45/80]
  [movement area]               [3 Nari 90/90]
                               Swap ready

Use narrow instruments and two compact controls, without a title or introduction. Assume no established brand: warm charcoal instrument surfaces, ivory text, muted jade HP/XP fills, and vermilion threat wedges with directional shapes. Use one legible sans-serif; make time and HP numerals tabular. Keep terrain colors independent of HUD styling.

Each standby control contains portrait/name, HP bar and numbers, and its keyboard key. Use WASD/arrows for movement and 1/2/3 for character selection; selecting the active character does nothing. Touch uses a left movement pad and right swap targets at least 56 pixels square, clear of safe-area insets. Reserve movement space in the arena camera composition.

A successful swap updates active status and both standby identities together. Show the shared cooldown beneath both targets as “Swap 0.8 s”; restore “Swap ready” after 1.25 seconds. Preserve HP visibility throughout. Attacks require no button. Retain text and shape cues alongside color; avoid pulsing warnings and respect reduced motion.

Unverified: readability during crowded combat, thumb occlusion and large-screen eye travel. Check these with moving gameplay before treating this layout as validated.

B. Search button

Keep the visible 36-pixel button and its layout box unchanged. Extend its clickable region using an absolutely positioned pseudo-element, four pixels above and below; also ensure at least 44 pixels of clickable width. Verify pointer/touch activation in the added area, unchanged appearance and surrounding positions, keyboard activation/focus, and no overlap with neighboring controls. No other changes.
