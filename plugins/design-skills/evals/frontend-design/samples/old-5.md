A. Build brief: “Daylight evacuation”

Use a sun-bleached battlefield with ink-dark silhouettes, chalk-white HUD plates and a single vermilion danger accent. The identity is practical emergency equipment: blunt lettering, clipped corners and conspicuous warning stripes. Remove the introductory label and poetic heading. The battlefield opens immediately.

Composition, landscape:

  LEVEL 06 ━━━━━━━ XP 72% ━━━━━━━━━━━━━━━━━
  │                                      ▲
  │            playable field            │
  │                                      │
  │                                      │
  [movement]                  [2 MIRA READY]
  SURVIVE 02:18               [3 ADELA READY]
                             [1 ACTIVE 68/90]

Anchor an asymmetric team selector at the lower right. The active character gets one large circular portrait with a thick HP arc and numeric HP. The two waiting teammates occupy compact horizontal tabs above it, each with portrait, name, individual HP bar and keyboard number. These are different roles, not three equal cards. Clicking a reserve tab or pressing its number swaps immediately; the current character takes its place.

A shared cooldown strip spans both reserve tabs. After any swap, it drains from 1.25 seconds to zero, displaying the remaining tenths and disabling both swap actions. Both tabs then say READY. Defeated teammates display OUT with a crossed portrait and remain unavailable. Never imply that a healthy reserve is ready while the shared cooldown is running.

Keep survival time large and stationary at lower left. Run experience along the upper edge, with explicit level and percentage. Attacks remain automatic; omit an attack button.

Nearby enemies retain strong silhouettes and ground shadows. Off-screen threats produce directional edge wedges; immediate threats use larger striped wedges. Combine shape and contrast with color, and keep warning marks clear of controls.

Use Barlow Condensed for time and numerals, Source Sans 3 for labels. Reserve animation for a brief active-portrait transfer and the cooldown drain; respect reduced motion. Build from flat vector primitives, with no decorative asset dependency.

Desktop: WASD/arrows move, numbered tabs swap. Landscape touch: a lower-left movement pad and two reserve targets at least 56 pixels high, inset from screen edges. Preserve the central battlefield and use the same selector states. Check HP, readiness and approaching danger during movement at the smallest supported landscape size.

B. Authorized button edit

Keep the button’s visible 36-pixel height and existing layout box. Extend its transparent pointer hit region 4 pixels above and below, producing a 44-pixel target; ensure its width is also at least 44 pixels. Keep the region attached to the existing native button and existing action.

Verify clicks in both added strips activate search once, keyboard activation still works, and the enlarged region does not overlap another interactive target. Compare before/after screenshots and element bounds to confirm the button’s appearance and surrounding positions are unchanged.
