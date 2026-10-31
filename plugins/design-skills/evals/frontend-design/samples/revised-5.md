A. Survival-action HUD

Required: three individual HP values, one active character, two swap targets, shared 1.25-second swap cooldown, remaining time, experience and nearby danger. Attacks stay automatic. Keyboard and landscape touch must work. Previous placement and copy are provisional.

Two structural candidates

1. Split perimeter

[Active portrait + HP]       [Reserve B: HP / ready]
[Time remaining]   PLAY      [Reserve C: HP / ready]
[Experience]       FIELD

The active character anchors attention on the left; swap actions occupy the opposite edge. Danger appears within the field and at its edges. Keyboard shortcuts appear beside reserves; touch uses those same large targets with movement at lower left. This preserves vertical play space but makes players scan between three regions.

2. Bottom instrument band

             PLAY FIELD
      nearby threats + edge warnings
[ACTIVE: HP==========] [Time] [B: HP / swap] [C: HP / swap]
[Experience===========================================]

Threats get first attention; a single glance downward covers survival status and switching. The active character receives a long HP bar, reserves receive compact action buttons, and time sits between them. Touch movement sits above the band's left edge; swaps remain within right-thumb reach. This costs vertical play space but groups decisions and actions together. Unlike the split perimeter, telemetry and swap controls share one continuous lower region.

Recommendation and build brief

Build candidate 2 under the existing authorization. Use current character portraits and game art. Give the band a warm gray surface with dark text; keep HP numerals and bar outlines readable against every arena background. Use teal plus “Ready” for availability, amber plus a numeric countdown for cooldown, and a distinct outline plus “Active” for the controlled character. No promotional heading.

Both reserve buttons show their own HP and the same shared countdown after a successful swap. Expose the configured keyboard bindings beside them. Start with 64 × 56-pixel touch targets and visible focus states; keep controls clear of device safe areas. Movement remains available during cooldown. Do not add an attack button.

Show nearby enemies through unobscured field rendering; use directional edge indicators for threats outside the visible field. Do not cover the player with status labels. Put remaining seconds and current experience progress in explicitly labeled readouts.

Required behavior is fixed; band placement, colors and target dimensions are recommended implementation choices. Exact movement controls and unavailable-teammate rules remain unspecified. Validate crowded combat, damage, simultaneous cooldowns, keyboard focus, text contrast and thumb occlusion at desktop and landscape sizes. These sketches establish no gameplay validation.

B. Search button hit area

Keep the visible button and its layout box at 36 pixels. Extend its existing clickable element's hit region by four pixels above and below using an absolutely positioned transparent pseudo-element. Verify a minimum 44-pixel hit height, unchanged neighboring positions and appearance, edge clicks activating the original action, no overlap with adjacent targets, and unchanged keyboard/focus behavior. If neighboring targets occupy that space, the stated constraints need reconciliation before implementation.
