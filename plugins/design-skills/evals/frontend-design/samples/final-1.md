A. Survival-action HUD

Required in both directions: one moving character, two available swap destinations, individual HP, a shared 1.25-second swap cooldown, automatic attacks, remaining time, experience and nearby danger. Preserve an open movement view. The old heading, English label and placements are provisional.

Two structural candidates:

1. Field-centered HUD
   Upper-left: remaining time + experience progress.
   At the character: active HP, immediately adjacent to incoming danger.
   Lower-right: two compact teammate swap buttons, each with HP.
   Between those buttons: one shared cooldown indicator.
   Lower-left: movement area on touch.

   Attention starts with the moving character and threats. Swap decisions travel from active HP to the waiting pair; all run information stays visible. Keyboard shortcuts appear inside the swap buttons. This replaces three equal roster cards with an active character embedded in play and two actionable reserves. Tradeoff: character-attached HP can obscure enemies unless its footprint and contrast are carefully controlled.

2. Fixed squad console
   Playfield occupies the left; a narrow right rail contains:
   remaining time / experience
   ACTIVE: prominent portrait and long HP bar
   two smaller waiting rows: HP + swap action
   one cooldown strip spanning both waiting rows

   Attention stays on play, with every squad decision collected in one stable scanning column. Nearby danger remains visible in the field. Keyboard shortcuts and touchable waiting rows provide direct swaps. Unlike candidate 1, active status joins reserve status in a persistent console. Tradeoff: stable status locations cost playfield width, and upper rail controls are harder to reach on landscape touch.

Recommendation and build brief: implement candidate 1 under the existing authorization. It gives the active character greater priority and puts both swap destinations within right-thumb reach. Compared with the old top-timer/three-card sketch, HP follows its subject and the roster becomes an action cluster.

Implementation choices: use restrained outlined HP bars and readable numerals; omit promotional copy. Keep all three HP values visible. Mark the active character explicitly. During cooldown, disable both swaps together and show one countdown; afterward mark both “Ready.” Label buttons with actual character names and keyboard bindings. Use at least 44-pixel touch targets. Represent nearby danger through actual threats and restrained directional cues; never rely on color alone. No attack button is needed.

Assumption: the existing movement scheme can coexist with lower-right swaps. Unverified: HP occlusion, threat readability during motion, thumb reach and keyboard focus. Check these with low-HP, cooldown and crowded-combat states. The fixed console remains an alternative, not an additional deliverable.

B. Search-button hit area

Keep the button’s visible 36-pixel height and layout box. Add a transparent, absolutely positioned hit extension on the same button: four pixels above and below, extending horizontally only if needed for a 44-by-44-pixel target. Preserve its label, styling, focus and activation behavior.

Verify actual clickable bounds, no neighboring-target overlap or interception, unchanged surrounding positions, and unchanged mouse, touch and keyboard activation. These checks remain unperformed in this text-only brief.
