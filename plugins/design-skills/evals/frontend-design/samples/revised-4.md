A. Survival HUD

Requirements: movement, three individual HP values, two reserve swap actions, shared 1.25-second cooldown, automatic attacks, remaining time, experience, nearby danger, keyboard and landscape touch support. Previous placement and wording are provisional. Assume movement and swapping are the only manual combat inputs.

Two structural candidates:

1. Split controls around an open arena. Active HP sits above movement at lower left; reserve HP and swap buttons stack at lower right. Remaining time occupies the low center, with experience along the bottom edge. Danger appears beside visible threats and as directional edge warnings. Attention starts with the character and threats, then travels to the relevant hand's control. Keyboard uses WASD and Q/E; touch uses a left stick and the two right buttons. All combat information stays visible. Tradeoff: eyes cross the arena to compare active and reserve HP, but touch controls have clear thumb zones.

2. One compact instrument spine on the left. Time, experience and active HP lead into two reserve rows containing HP, readiness and swap actions. The arena occupies the remaining width; danger warnings stay at its perimeter. Keyboard players scan one column and press Q/E. On touch, reserve rows are tappable above the movement stick. Tradeoff: comparing the team is easier, but swapping and moving compete for the left thumb and the narrower arena changes threat visibility.

The structural difference is distributed information adjacent to each hand versus one consolidated team/status column. Recommend candidate 1 for simultaneous movement and swapping on touch; proceed with this direction under the existing authorization.

Next designer's build brief:

- Required behavior: show numeric HP plus bars for every character. Keep the active character unmistakable. Each reserve button names its teammate; use Q/E labels on desktop. Both buttons display the same remaining cooldown after a swap. Show “Ready” when available; make unavailable states legible without color alone. Attacks need no button.
- Recommended composition: unequal control groups around a large arena, with no introduction or promotional heading. Use a restrained warm-gray HUD surface, dark text and a single readiness accent; danger uses a distinct shape and color. Preserve readable contrast against changing scenery. Reserve touch targets are at least 48 pixels with separation. Respect safe areas and reduced motion.
- Remaining options: art-specific colors and typeface. Keep these flexible until actual environments are supplied.
- Unverified: gameplay readability, thumb reach and occlusion. Check identical crowded-combat states on desktop and landscape touch, including low HP, cooldown, teammate defeat and XP changes. No rendered or interaction checks were performed here.

B. Search button

Keep the 36-pixel visible button and its layout box. Extend its clickable region four pixels above and below using an absolutely positioned transparent button pseudo-element: 44 pixels total, with width at least 44 pixels. Preserve its label, styling, focus behavior and handler.

Verify unchanged surrounding positions and appearance; clicks in both added strips activate search once; keyboard activation remains intact. Check ancestor clipping and overlap with adjacent targets. These are proposed checks, not completed tests.
