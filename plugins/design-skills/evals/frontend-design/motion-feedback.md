# State feedback and functional motion smoke check

Date: 2026-11-03. Baseline repository commit: `55f6213229b521da0db30818b010724b339cbceb`.

## Procedure and limits

Before editing the skill, the author recorded the brief and criteria below, then requested one application response using a copy of the current skill. A second fresh agent received the same brief with the final revised skill. Agents were dispatched with no conversation history and asked to read only their supplied guidance, the brief, and references actually routed to by that guidance. Neither was given the criteria or the other response. Both reported no access limitations. The brief, criteria body, and complete responses are preserved below with terminal whitespace normalized; the criteria's original heading, "Criteria recorded before skill edits," is shortened to "Criteria." The skill inputs are identified by hashes rather than embedded.

This is one text-specification response per condition, each covering the same two synthetic interfaces. These agents share the parent runtime and can encounter its skill catalog and instructions; no-history dispatch does not establish a clean experimental control. The author read both responses and was not blinded. Model identifiers and sampling settings were not independently recorded. No UI was implemented or rendered, no user study was run, and automatic skill selection and installation were not tested.

The concrete tasks are evaluation inputs only. They are not examples or a component catalogue in the runtime skill. The earlier structural evaluation is a separate historical record and is not re-scored here.

## Observations

Both responses cover pending versus confirmed reservations, rejection, updates from other people, stale availability, preservation of the user's place, and reduced motion. Both avoid fabricated percentages and completion estimates. Both keep synchronous archive navigation immediate and indexing updates quiet. No baseline failure was demonstrated against the recorded criteria.

The baseline chooses steady pending text; the revised response permits an optional activity cue alongside persistent text, explicitly stopping it if confirmation becomes unknown. More motion is not scored as better behavior. In both responses, useful state remains available without animation.

This check found no obvious conflict between the revised guidance and these application tasks. It does not establish improved detection, a causal guidance effect, generalization, consistency across repeated runs, or better usability. The change makes the user-approved decision criteria explicit; those outcomes would need broader independent evaluation.

## Input hashes

SHA-256 hashes refer to the complete source files read or written in this run, before the terminal-whitespace normalization used for embedding them below.

- Baseline SKILL.md: `cd8da638e31378ffa412d7680f3abad8c1b09115d1c8703ed6841b07fc32a2d2`
- Revised SKILL.md: `1c550eabe98af616cceb94a0c638343aaed64e398be966cc4915eb93c0ef7a0e`
- Brief: `e12956447ae4e60bcdc2a2fd839160a19a7e8ed02fd06bc93bbc0a010710f2ee`
- Criteria: `72747aa21c455d2fc6c0e1dcac52125f243a4fc02632cf37671270bf6fac651f`
- Baseline response: `ded1543dce9f7abbbbb397bb59a60d15a64a8eb893c35ebb9b01e84fc2331483`
- Revised response: `82f02a74236367253f837525df67c790b7deb45234e23796f4dd19fdcf782b4b`

## Brief

Write a concise interaction specification for these two already-approved interfaces. Keep their layouts and feature sets. Explain the visible behavior over the course of use and what that behavior communicates. Do not implement code. Stay within 400 words total.

A. A shared equipment reservation board. A user's change may wait for server confirmation for several seconds. The server can reject it when another person reserves the same item. Changes made by others can arrive while this user is reading the board. While disconnected, the client retains its last received board; there is no authoritative current availability or completion estimate. The user needs to make a reliable reservation without losing their place.

B. A local archive reader. Moving between a list and a document completes synchronously. Both views have stable, clearly labeled navigation. A background indexing count can change several times per second, but does not affect the document being read or require action. The reader needs to maintain orientation and focus, including when the operating system requests reduced motion.

## Criteria

Read complete responses for user-visible behavior, not matching words or a mandated component.

- Does the proposal communicate consequential state throughout the user's task, including intervals and changes not caused by the user's current action?
- Does it distinguish local intent, authoritative confirmation, conflict, and stale knowledge without inventing measured progress or healthy processing?
- Is each proposed functional animation justified by information it communicates, with static feedback allowed where sufficient?
- Does it preserve orientation and useful status with reduced motion, without distracting motion for irrelevant activity?
- Does it preserve the approved layout and avoid inventing features or forcing an approval loop?

This is a bounded text-specification smoke check, not a usability experiment. Shared runtime context may affect both conditions. A successful baseline is recorded as such; no failure or improvement is inferred from the wording alone.

## Baseline response

A. Shared equipment reservation board

Keep the approved board layout. Submitting a reservation leaves the user at the same item and scroll position. The affected action immediately shows “Awaiting confirmation” and prevents duplicate submission. Preserve the requested selection while waiting; availability remains unconfirmed. A steady status message is sufficient. Do not imply progress or promise a completion time during a several-second wait.

Only server acceptance produces “Reservation confirmed” and the confirmed board state. Announce the result without moving keyboard focus. If another person wins the reservation, replace the pending state with a clear explanation: “This item was reserved by someone else. Your reservation was not made.” Retain the user's place so they can review remaining choices.

Other people's updates change the affected availability in place. Avoid automatic reordering, scrolling, or focus changes while the user reads. Briefly distinguish an updated item, with a textual status as well as any visual emphasis; do not repeatedly animate the board or announce every incoming change.

On disconnection, retain the last received board and visibly identify it as out of date. Do not present retained availability as current or treat an unresolved request as successful or rejected. Explain that confirmation requires reconnection. On reconnection, reconcile with the server before presenting availability or reservation outcomes as current. Preserve focus and reading position throughout. Reduced motion removes decorative transitions without suppressing status information.

B. Local archive reader

Opening a document or returning to the list changes views immediately, with no loading indicator or artificial delay. Stable navigation labels and the document title identify the destination. Opening a document places keyboard focus at its reading heading; returning restores the originating list item's focus and the list's scroll position. Navigation remains usable without animation.

If existing view transitions are retained, keep them brief and subordinate to the immediate navigation result. Under reduced motion, replace movement with an immediate view change; retain the same content, focus handling, and navigation cues.

Indexing stays in its existing status area. Present the latest count at a calm, readable cadence rather than animating each increment. Do not move content, steal focus, interrupt reading, or announce each count update. The count communicates background activity, not a task the reader must attend to.

## Revised response

**A. Shared equipment reservation board**

Keep the approved layout. On submission, retain the selected item, scroll position, and keyboard focus. Show “Awaiting confirmation” beside the attempted reservation; prevent duplicate submissions while leaving unrelated board navigation usable. Pending status is visually distinct from a confirmed reservation. Do not show a completion percentage or estimated remaining time.

While connected, a small indeterminate activity cue may accompany that label to communicate waiting, without implying measured progress. Under reduced motion, the persistent text communicates the same state.

Only a successful server response changes the reservation to confirmed. Replace pending feedback with a clear confirmation tied to that item. If the server rejects a conflict, show “Another person reserved this item. Your reservation was not made.” Keep the user in place and make the item’s returned availability visible. Announce the outcome accessibly without moving focus.

Apply incoming changes from others without resetting scroll, stealing focus, or unnecessarily moving items. Briefly identify changed availability through text or a persistent visual marker; do not rely on a transient flash. Announcements should be concise and avoid interrupting reading.

On disconnection, label the retained board as the last received information, with its actual receipt time if known. Availability is unverified; new reservations cannot be confirmed. If connection is lost after submission, show “Confirmation unknown” rather than success or failure, and stop the activity cue. On reconnection, reconcile the pending attempt with server state before allowing a duplicate attempt or claiming an outcome. Keep stale status until fresh information arrives.

**B. Local archive reader**

Switch directly between list and document: synchronous navigation needs no loading indicator or transition. The existing labels establish the destination. On opening, move keyboard focus to the document heading; on return, restore the originating list item, its focus, and scroll position.

Keep indexing feedback visually quiet and spatially stable. Display the latest count at a readable cadence rather than animating every increment; do not pulse, resize surrounding content, or announce every change. Indexing updates never move document focus or scroll. The count communicates background work, not a reason to interrupt reading.

These behaviors also apply with reduced motion: orientation, status, and focus remain explicit without animation.
