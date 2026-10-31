A. Survival-action HUD

Required: one moving character, two waiting teammates, individual HP, shared 1.25-second swap cooldown, automatic attacks, remaining time, XP, nearby danger and teammate readiness. Support keyboard now and landscape touch later. Previous positions, equal cards and heading copy are provisional.

Two compact directions:

1. Field-linked HUD. Put active HP beneath the character, with nearby threats clearly outlined in the world. Two waiting portraits with HP and swap controls sit at lower right; a single cooldown band connects them. Remaining time and XP occupy a narrow bottom strip. Attention stays on survival; movement → glance toward a teammate → swap. Touch movement goes lower left. Tradeoff: active HP moves through busy scenery and needs an opaque backing.

2. Roster rail. A compact left rail combines remaining time, XP and three stable character slots: an enlarged active slot above two smaller waiting slots, each with HP. Waiting slots expose swap readiness and a shared countdown. Nearby danger remains in the world. Movement → scan the rail → choose a waiting slot. Touch movement sits below the rail. Tradeoff: stable status positions simplify scanning, but draw attention away from the character and consume horizontal space.

Recommendation: field-linked HUD. Unlike the previous timer-over-three-equal-cards sketch, it separates immediate survival from teammate selection and makes the shared cooldown visibly connect its two affected actions. Compared with the rail, its decisive difference is active HP adjacent to the moving character, while only actionable teammates occupy the fixed dock. Proceed with this direction under the existing authorization.

Next-designer build brief

Selected composition:

  [                 combat field                 ]
  [                character                     ]
  [                 HP                           ]
  [move zone                  teammate B / C      ]
  [remaining 02:14        XP =================    ]

Use existing portraits and restrained flat panels; omit promotional headings. Use warm white labels on opaque charcoal backings, HP bars with numbers, and amber threat outlines. Reserve red for damage/critical HP. Readiness also needs text and shape, not color alone.

Keep character identities assigned to stable keys 1–3. Show the corresponding key on each waiting portrait. On touch, provide a left movement pad and two right swap targets, at least 48 pixels each. Attacks need no button.

After any successful swap, both targets display the same countdown from 1.25 seconds and reject activation until ready. Display “Ready” when available; preserve each character’s HP through swaps. Do not let the dock obscure nearby threats.

Unresolved: exact safe margins and portrait scale. Unverified: readability during crowded combat, thumb reach and keyboard discovery. Check these at desktop and landscape sizes, including critical HP and cooldown expiry.

B. Search button

Expand its interactive box by four pixels above and below, producing a 44-pixel hit area; retain the centered 36-pixel visible surface and existing layout footprint. Use invisible overflow owned by the same button.

Verify edge taps, keyboard activation, unchanged appearance and surrounding positions, and no clipping or overlap with neighboring targets. No implementation or checks performed here.
