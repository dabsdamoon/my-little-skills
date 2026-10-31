A. Survival HUD

Required: three individual HP values; one active character; two swap destinations; shared 1.25-second swap cooldown; remaining time, experience and nearby danger. Attacks remain automatic. Support keyboard now and landscape touch later. Previous placement and promotional copy are provisional.

Two directions:

1. Field-local HUD. Active HP follows the controlled character with a small, stable offset. Two reserve buttons sit at the right edge, each showing portrait, HP and readiness. Remaining time and experience occupy a quiet upper-left readout. Danger indicators sit beside threats, with directional edge markers for nearby danger outside the viewport. Keyboard swaps or a single thumb tap directly select a reserve. This keeps survival feedback near movement; the moving HP indicator needs careful overlap handling.

2. Instrument shelf. A continuous bottom band contains a prominent active-character HP gauge, then time/experience, then two reserve buttons with HP and readiness. Danger stays in the playfield. Keyboard and direct touch selection use the same destinations. Everything except danger is stationary and grouped for scanning, but the shelf takes more playfield height and pulls attention downward.

Their structural difference is distributed, character-relative feedback versus one persistent dashboard, not simply different colors or exchanged positions.

Recommendation and build brief: implement direction 1 under the existing authorization. Compared with the previous three equal cards, it separates immediate survival from roster management and makes the active character visibly primary. Omit the label and poetic heading: begin directly in play.

Use compact portrait silhouettes, warm ivory text and charcoal backing plates with clear outlines; retain the game's existing world palette. Shape and text accompany status colors. Both reserve buttons show “Ready” when available; after a swap, both show the same countdown from 1.25 seconds. At zero, restore “Ready.” A defeated teammate shows “Down” and cannot be selected. Show active and reserve HP numerically alongside bars. Experience includes progress and level; time uses mm:ss.

Keep reserve targets at least 48 × 48 pixels, clear of movement input. Show their actual keyboard bindings. Keep danger cues clear of the local HP gauge. Use restrained depletion animation, respecting reduced motion.

Required behavior stays fixed; these positions and styling are recommended implementation choices. No alternative requires another approval meeting. Unverified assumptions: the field supports a local HP overlay and right-side controls. Check crowded combat, shared cooldown transitions, keyboard focus, contrast and landscape thumb reach in a playable build; no rendering or usability checks were performed here.

B. Search button

Preserve its existing layout footprint and 36-pixel visible face. Extend its transparent pointer target four pixels above and below using an absolutely positioned pseudo-element belonging to the same semantic button; extend horizontally too if needed for 44 × 44 pixels.

Verify the expanded area activates the existing action, is not clipped or overlapping another control, preserves keyboard operation, and leaves visible geometry and surrounding positions unchanged. These checks remain unperformed.
