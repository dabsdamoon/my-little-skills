A. Survival-action HUD

Direction: a bright arcade field with an asymmetric “rescue dispatch” overlay. Use warm ivory panels, ink-blue numerals and coral threat marks against a sunlit, desaturated arena. Remove the introductory heading and decorative English label: the playfield starts immediately. Avoid a row of character cards.

Desktop wireframe:

[ACTIVE portrait · key 1 · HP 82/100]      [pause]

                 OPEN PLAYFIELD         [2 portrait]
                 player + enemies       [HP 61/100]
                                        [READY]
                                        [3 portrait]
                                        [HP 90/100]
                                        [READY]

[XP 73% ━━━━━━━━━]       [REMAINING 04:32]

The active character’s HP is the strongest HUD signal: a wide bar with its exact value, portrait and name. The two waiting teammates occupy a narrow right-edge swap rail, each with an individual HP bar and persistent character number. Their portraits remain visually subordinate to the active HP display.

Press 1/2/3 to select a character; WASD moves; attacks happen automatically. Each reserve portrait is also a button. A successful swap updates the active panel and reserve rail immediately. During the shared 1.25-second cooldown, one bracket spanning both reserve buttons fills down, displays the remaining tenths, and replaces READY with WAIT. Keep both HP values visible. Restore READY and the button outline together when swapping becomes available. Use text and shape as well as color.

Nearby danger lives in the arena: crisp enemy silhouettes and ground attack telegraphs. For threats just outside view, use short inward-pointing wedges at the corresponding screen edge; increase wedge size with proximity. Keep the player’s immediate surroundings free of HUD panels.

Landscape touch: retain active HP at upper left. Place a movement pad at lower left and the reserve rail at lower right, with two 64-pixel portrait buttons and 12 pixels between them. Move XP and remaining time into the bottom-center gap. Respect device safe areas; keep telegraphs visible beneath translucent controls. Pause has a 48-pixel target.

Build brief: deliver one responsive HUD composition and its active, ready and shared-cooldown states. Use a single UI font with tabular timer digits, restrained diagonal panel corners and no ornamental title area. Prioritize legibility in motion. Check HP loss, both swap directions, simultaneous cooldown feedback, dense enemy scenes and the smallest supported landscape viewport. Proceed with this direction; no additional approval meeting is needed.

B. Library search button

Keep the visible button at 36 pixels and preserve its layout box. Extend the existing button’s interactive region vertically by 4 pixels above and below, using an absolutely positioned transparent pseudo-element attached to that same button. Ensure its hit width is also at least 44 pixels, without changing layout.

Verify the computed hit region is at least 44 × 44, all added edges activate search, and no clipping or overlap steals adjacent controls’ input. Confirm surrounding positions, button appearance, keyboard activation, accessible name and tab order remain unchanged.
