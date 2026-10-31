A. Survival-action HUD

Requirements: one moving character, two waiting teammates, individual HP, automatic attacks, a shared 1.25-second swap cooldown, remaining time, experience, nearby danger, and explicit swap readiness. Support desktop keyboard and future landscape touch. The old layout and copy are provisional.

Two directions:

1. Left command rail
A narrow vertical roster anchors the left edge. The active character gets a larger HP row; the two waiting characters have compact swap buttons with HP and readiness. Time and experience sit beneath the roster. Danger indicators occupy the corresponding playfield edges. Attention moves from combat to one consolidated status column; keys 1–3 or tapping a roster row select a character. This leaves the bottom clear but competes with the left thumb on touch screens.

2. Bottom command shelf — recommended

    [danger chevrons at threatened edges]
                  PLAYFIELD

    [Remaining 02:41]    [Experience 65%]
    [move zone] [ACTIVE: Mira / HP 72%] [Adela 45%] [Nari 90%]
                                            Ready       Ready

The active character's wide status strip separates movement on the left from two adjacent swap targets on the right. Time and experience form a thin strip immediately above. Danger stays beside the world location requiring attention. The main path is move, glance at active HP, then select either waiting teammate. Combat receives first attention; the shelf provides one predictable glance destination. It consumes bottom height but keeps swapping within right-thumb reach.

The structural difference is a vertical roster combining all status versus a horizontal action surface separating movement, active health, and waiting teammates.

Next-designer build brief:

Required behavior: preserve every state above; automatic attacks need no attack button. Use stable roster keys 1–3, displaying each key beside its character. Keep every character's HP visible. During cooldown, both waiting targets show the same countdown, such as “Swap in 0.8s”; when available, both show “Ready.” Identify the active character with text and shape, not color alone. Do not shift controls when swapping.

Recommended implementation choices: build direction 2 with solid warm-gray panels, charcoal text, restrained teal readiness, and red danger/critical-health signals reinforced by symbols. Use plain labels and one readable type family. Touch adds a left movement pad; maintain generous spacing and at least 48px swap targets. Keep indicators clear of controls and safe-area insets.

Unresolved: exact shelf dimensions. Unverified: thumb reach, combat occlusion, danger readability in motion, and keyboard focus. Test these with all HP levels, both cooldown states, and dense combat before polishing.

B. Search button hit area

Preserve its existing layout slot. Position a native 44px-high button centered over that slot, with transparent 4px top/bottom padding surrounding the unchanged 36px visible surface. Preserve width unless below 44px; then extend the transparent hit area symmetrically.

Verify unchanged neighboring positions and visible pixels, successful clicks throughout the added area, no intercepted neighboring targets, and unchanged keyboard activation and focus treatment. These checks are specified, not executed.
