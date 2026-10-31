A. Survival-action HUD

Required: one moving character, two swap destinations, three separate HP readings, shared 1.25-second swap cooldown, automatic attacks, remaining time, experience, and nearby danger. Support keyboard now and landscape touch later. The old heading, cards, colors, and positions remain provisional.

Three compact directions:

1. Bottom instrument rail
Arena above; a continuous bottom strip joins a large active-character HP gauge, time/XP, and two smaller reserve controls. Keyboard numbers select characters; touch puts movement above the left end and reserve taps at the right. Danger stays visible in the arena with edge warnings. Everything is gathered for fast scanning, but the rail consumes vertical combat space.

2. Split cockpit
Active HP anchors the upper left. Time and XP form a compact upper-right readout. Two reserve controls occupy the lower right, leaving the lower left for touch movement. Each reserve shows its own HP and availability. Nearby danger is read around the character and at the arena edge. Keyboard selection and reserve taps share the same controls. This preserves a broad central playfield; checking the whole team requires a longer eye movement.

3. Team ladder
A narrow left column contains all three characters: active row expanded, reserves compact and selectable. Time and XP sit beneath the column. Keyboard selection or row taps swaps characters; touch movement sits below the column. Danger remains in the arena and its perimeter. Team condition is easiest to compare, but the column narrows the horizontal view and places swaps farther from the right thumb.

Recommendation and build brief: implement the split cockpit under the existing authorization. Its controls fit landscape thumbs while the arena retains priority. Unlike the rail, it distributes information by task instead of collecting it in one band.

Use warm bone-colored gauges and charcoal text on compact opaque backplates, with danger in vermilion. Use the project's language-capable UI font, sentence-case labels, and large timer numerals; omit promotional copy. Keep enemy silhouettes legible against terrain.

Active HP reads “Name 72/100.” Each reserve control includes name, HP, and “Ready,” “Active,” or the shared remaining cooldown. After a swap, both reserve controls show the same countdown; zero restores readiness together. HP must remain readable beneath cooldown treatment. Use at least 48-pixel touch targets. Bind 1/2/3 to direct character selection and show those hints on desktop. Attacks need no button.

Required behavior stays fixed; these positions and styling are recommended implementation choices. Preserve existing unavailable-character rules. Validate low HP, simultaneous danger/cooldown, longest names, keyboard focus, and landscape touch overlap. Gameplay readability and thumb reach remain unverified until playtested.

B. Library search button

Keep the 36-pixel visible button and layout box. Add an absolutely positioned, transparent, pointer-active pseudo-element extending four pixels above and below, and horizontally if needed to reach 44 pixels wide.

Verify the computed hit region is at least 44×44, taps in the added area activate search once, adjacent controls remain reachable, keyboard behavior is unchanged, and screenshots and element bounds confirm no visible or positional change. No checks have been executed.
