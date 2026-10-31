A. Survival-action HUD

Direction: a sunlit expedition wayfinder. Warm limestone terrain, deep petrol ink, and hot orange danger marks replace the dark field and card row. No heading or introductory copy: the battlefield opens immediately. The memorable element is a three-point team compass anchored beside the player’s thumb.

I considered a full-width arcade instrument strip, but its continuous frame would compete with the landscape. Build the compact wayfinder instead; its asymmetric silhouette leaves more of the playfield visible.

Landscape sketch:

  XP  ━━━━━━━━━━━━━━━────────  LV 7

              playable field
        ↘ nearby danger markers

                       [reserve B]
  movement zone        [ACTIVE A] [reserve C]
                       HP 76/100
             08:42 remaining

The sketch indicates relationships, not a requirement to place controls over enemies. Reserve a clear camera-safe margin around the HUD.

The active character gets a large portrait disk and a prominent individual HP arc. Each reserve gets a smaller portrait, its own HP bar, and explicit READY text when swapping is available. Never collapse team health into one meter. The compass is a compact cluster, not three equal cards.

Click or tap a reserve portrait to swap. Desktop portraits also show their direct-selection keys, 1–3. Keep their locations stable when the active character changes; change prominence and the active marker instead. During the shared 1.25-second cooldown, both reserve targets show the same countdown and sweep, then READY. Do not imply separate cooldowns. Automatic attacks need no button.

Place remaining time at bottom center in large tabular numerals. Run XP along the upper edge with a level label and a visible progress endpoint. Nearby danger uses inward-facing wedges at the relevant screen edge, with size and pulse indicating proximity; actual nearby enemies remain visible. Shape and motion reinforce color, so orange is never the only warning.

Build brief: use Barlow Condensed for timer and numbers, Atkinson Hyperlegible for labels, solid surfaces, crisp outlines, and almost no shadows. Keep danger and HP legible against every terrain value. Touch swap targets are at least 56 pixels; leave a lower-left movement zone and test thumb reach in landscape. Ship one brief swap pulse and the cooldown sweep; support reduced motion. Verify three unequal HP values, swapping through the full cooldown, XP changes, crowded danger, keyboard operation, and touch overlap. Proceed with this direction without another approval round.

B. Search button hit area

Keep the visible 36-pixel button and its layout box unchanged. Extend its clickable area by 4 pixels above and below using an invisible positioned hit layer belonging to the same button. Extend horizontally too if its width is below 44 pixels.

Verify a minimum 44 × 44 target, successful clicks in the added area, unchanged surrounding coordinates and appearance, and unchanged keyboard activation and focus behavior. Check that clipping or neighboring controls do not obstruct or overlap the extension.
