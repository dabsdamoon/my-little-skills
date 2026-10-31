The decision to support is: can the current character survive nearby pressure, and which reserve is worth spending the shared swap window on? Individual HP, automatic attacks, time, XP, nearby danger, keyboard control, and future landscape touch remain required.

Two inexpensive directions:

- **Squad rail:** Put three fixed character slots together along the bottom, each combining portrait, HP, and selection action. Mark the active slot clearly; one shared cooldown bar spans the entire group. Nearby danger stays beside the player; time and XP share a quiet top strip. Players compare all three HP values, then select a reserve in the same place. This consolidates the decision but draws health checks away from the moving character.
- **Roster and command split:** Put a compact, persistent three-character health roster at the top, with the active character emphasized. Two large reserve selectors sit within the right thumb’s reach, labeled to match the roster; their enclosing frame shows the shared cooldown. Danger remains local, and time/XP occupy a narrow bottom strip. This protects large touch controls and open play space, but comparing HP and choosing a reserve requires looking between separate regions.

**Recommend the squad rail.** Against the accepted prototype—player-following active HP, two lower-right reserve buttons, edge time/XP—it changes the useful relationship: active and reserve health become directly comparable, and the comparison itself is actionable. This is more than relocating the existing widgets. The two candidates differ chiefly in whether squad information and swap actions occupy one shared surface or separate regions.

Implementation handoff:

- Keep slot positions stable across swaps. Show the active state through border, label, and shape; never rely on color alone.
- Map desktop keys 1–3 to the corresponding slots. Selecting the active slot does nothing; selecting a reserve swaps only when allowed. Keep movement and automatic attacks intact.
- Display the 1.25-second shared cooldown once across the rail, with remaining time and disabled reserve states. Preserve each character’s own HP.
- For landscape touch, use large fixed targets on the right half, leaving left-thumb movement space. Keep the player’s immediate danger cues unobstructed.

These are recommended implementation choices, not newly approved requirements. The split layout remains an alternative. Verify readability during movement, cooldown feedback, keyboard focus, and thumb reach; no rendered or gameplay validation has occurred.
