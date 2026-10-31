A. Survival-action HUD

Direction: a field instrument, with the arena doing most of the visual work. Use a pale mineral ground, charcoal silhouettes and sharp orange threat signals. Skip the introductory label and headline. The opening frame is already playable.

Compact landscape wireframe:

  XP 640 / 900 ━━━━━━━━━━━━━━━──────  LV 4
  MIRA • ACTIVE
  HP 82 / 100 ━━━━━━━━━──

                   ↑ nearby threat
           [open movement and combat field]
                                  ┌ ADA   HP 61/80 ┐
                                  │ 1  SWAP READY │
                                  ├ JUN   HP 30/90 ┤
                                  │ 2  SWAP READY │
          [touch movement]        └───────────────┘
                    03:42 REMAINING

The active character gets an unboxed identity and the strongest HP readout. The two waiting characters occupy compact, stacked swap tabs at the lower right; their HP remains readable without resembling three equal dashboard cards. Each tab is a direct action, not an informational panel with a second button inside it.

Swapping starts one shared 1.25-second lock. Both tabs immediately display the same countdown and a draining perimeter stroke. At zero, both show READY. Preserve reserve HP during this transition. After a swap, the outgoing character takes the selected reserve slot and the incoming character becomes ACTIVE. Use text and stroke changes alongside color, so readiness never depends on green alone.

Keep the timer fixed at bottom center with tabular numerals. The thin top XP ruler fills left to right and resets on leveling; retain numeric progress. No attack button: attacks are automatic.

Nearby danger belongs to the arena: clear enemy silhouettes, visible attack telegraphs, and edge chevrons pointing toward nearby threats beyond the viewport. Keep chevrons outside the central combat area; do not reveal distant enemies. Orange is reserved for danger, with explicit HP numbers distinguishing injured teammates.

Build brief: deliver one playable landscape HUD using this hierarchy. WASD moves; 1 and 2 select reserve slots. Touch adds a lower-left movement pad and enlarges the same reserve tabs to at least 72 pixels high, with safe-area padding. Keep the central field unobstructed. Verify individual HP, outgoing-slot behavior, synchronized cooldown, XP reset and timer readability during crowded combat. Treat this as the next build direction; no additional approval meeting is needed.

B. Search button hit area

Keep the button’s visible 36-pixel height and existing layout box. Extend only its interactive region by 4 pixels above and below using an absolutely positioned transparent hit layer attached to the existing button. Ensure its width is also at least 44 pixels.

Verify clicks across the full expanded area activate the existing action, surrounding elements retain their exact positions, visible styling is unchanged, and the extension neither clips nor overlaps another control’s hit region. Preserve the existing keyboard behavior and accessible name.
