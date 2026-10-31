A. Survival-action HUD

Required: one moving character, two swap targets, individual HP, one shared 1.25-second swap cooldown, automatic attacks, remaining time, XP, nearby danger and teammate readiness. Desktop keyboard and landscape touch must remain usable. The old composition and copy are provisional.

Two structural candidates

1. Spatial squad — recommended

  [Remaining 08:42]                   [XP 64/100]

           enemies → [PLAYER: HP ring]
                         ↑ danger cue

  [movement zone]               [Mira 72/100 • Ready • 1]
                                [Ada  38/100 • Ready • 2]

Attention starts with the player and immediate threats. Active HP follows the character; reserve HP and swapping share two compact, unequal-width rows near the right thumb. Time and XP occupy quiet corners. Move with WASD; press 1/2 or tap the corresponding reserve. Automatic attacks need no control. Tradeoff: the moving HP ring needs careful separation from enemy effects.

2. Instrument rail

  [TIME       ] |                                      |
  [XP         ] |             PLAYFIELD                |
  [ACTIVE HP  ] |                                      |
  [RESERVE 1  ] |                                      |
  [RESERVE 2  ] |                                      |

A fixed left rail groups all status and swap actions; nearby danger remains visible in the playfield, with directional warning marks when necessary. Keyboard movement and numbered swaps remain available; landscape touch uses movement at lower left and reserve buttons in the rail's lower section. All three HP values and the shared cooldown stay visible. Tradeoff: stable scanning costs arena width, and left-side swapping competes with the movement thumb.

The structural difference is active HP attached to the player with right-side actions versus all status/actions consolidated outside the arena. Recommend spatial squad: it connects health to the character being protected and separates movement from swapping. Compared with the previous three equal cards, active and waiting characters now have distinct roles and locations. Omit promotional headings.

Build brief

Required behavior remains as listed above. Implement the recommended layout under existing authorization; it is a recommendation, not a user-approved standard. Use legible sentence-case labels, neutral translucent backplates, and HP numbers alongside bars/rings. After swapping, update the ring and reserve identities; both reserve controls show the same countdown and become ready together after 1.25 seconds. Do not display contradictory readiness. Keep keyboard focus visible and touch targets at least 48 pixels. Avoid automatic decorative motion.

Assume direct teammate selection; unavailable-character rules remain unspecified. Validate dense combat, critical HP, cooldown transitions, long names and landscape thumb reach. No rendered or gameplay checks have been performed.

B. Search-button hit area

Preserve the 36-pixel visible button and layout footprint. Extend its interactive bounds four pixels above and below using an absolutely positioned transparent pseudo-element attached to the button; ensure width is also at least 44 pixels. Keep the existing handler, label and focus treatment.

Verify boundary clicks activate exactly once, keyboard behavior remains intact, neighboring targets do not overlap, expanded bounds are not clipped, and before/after geometry and appearance match. Checks are specified, not executed.
