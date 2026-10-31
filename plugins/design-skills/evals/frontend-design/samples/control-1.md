A. Survival-action HUD

Use a bright, utilitarian field-instrument direction: the game scene fills the screen, with warm ivory readouts, near-black text, cobalt selection marks and orange danger chevrons. No heading or introductory copy. The composition follows play: movement space on the left, teammate actions on the right, progression along the bottom.

Compact landscape wireframe:

[ACTIVE: MIRA | HP 78/100]                         [Pause]

                 PLAYFIELD
          directional danger chevrons
                                              [Q  JUN]
                                              [HP 42/80]
                                              [READY]
                                              [E  SOL]
                                              [HP 65/90]
                                              [READY]

[left movement zone]             [03:42 remaining]
[LV 7 |================ XP 62/100 =================]

The active character gets one horizontal health readout at upper left. The reserves form a narrow vertical action rail, visually smaller than the active readout. Use character portraits and names consistently; HP numbers and bars stay visible during every swap state. This replaces the three-card presentation with a clear active/reserve hierarchy.

Both reserve buttons display READY when swapping is available. After either swap, both show the same draining 1.25-second indicator and a tenth-second countdown; disable both until it expires. Keep button bounds fixed. The selected reserve becomes active, and the outgoing character occupies that same reserve slot. Briefly pulse the new active portrait so the change is clear.

Nearby threats stay legible in the scene. Draw short orange chevrons at the viewport edge only for dangerous enemies just outside view; point toward their world direction. Give immediately threatening attacks a distinct outlined ground warning. Never substitute a generic danger score for attack location.

Desktop: WASD/arrows move, Q/E activate the corresponding reserve slot. Attacks remain automatic. Landscape touch: reserve rail buttons have at least 56×64 logical-pixel targets within the right thumb area; a floating movement stick occupies the lower-left zone. Keep both zones free of informational overlays. Pause has a 48-pixel target. Use text and shapes alongside color for every state.

Build brief: ship these five reusable elements—active HP strip, reserve button, countdown, XP strip and threat marker. Use system sans typography, tabular numerals and simple vector shapes. No decorative animation beyond short state feedback. Check narrow landscape screens, low HP, overlapping enemies, both cooldown states and rapid swaps; the timer and every HP bar must remain readable.

B. Search button hit-area edit

Keep the approved button’s 36-pixel visible height, position and styling. Expand its interactive bounds by four pixels above and below, producing a 44-pixel-high target without changing layout dimensions. Preserve its existing width, expanding horizontally only if needed to reach 44 pixels.

Verify the added perimeter activates the same search action, including on touch; neighboring controls retain their own targets without overlap. Confirm surrounding coordinates, visible button appearance, keyboard activation, focus styling and tab order are unchanged. If adjacent hit areas overlap, stop and report the specific geometry conflict rather than altering the approved layout.
