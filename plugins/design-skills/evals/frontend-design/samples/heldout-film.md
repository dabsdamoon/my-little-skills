**Next-designer brief: a film society’s running program**

Assume visitors primarily use phones to find a suitable upcoming screening and book. No brand assets or real program were supplied; all examples below are fictional.

**Keep constant:** Every screening must expose its date, time, film, venue, remaining seats, plain-language accessibility details, and booking action. Support chronological browsing, readable contrast, keyboard access, generous touch targets, and capacity changes. The previous identical-card grid is a provisional layout, not a requirement.

Compare these inexpensive text sketches using the same screenings: *River*, 12 November at 18:00, Hall A, 8 seats, step-free access and captions; *Night Bus*, 12 November at 20:30, Studio B, sold out, stairs and no captions.

**A — Running-order ledger.** Attention starts with the next date, then follows a continuous time rail. Use shared date headings and ruled rows rather than separate containers.

```text
12 NOVEMBER
18:00  River                              Book
       Hall A · 8 seats
       Step-free · Captions
20:30  Night Bus                       Sold out
       Studio B · 0 seats
       Stairs · No captions
```

Visitors scan forward and book directly beside the chosen screening. Accessibility stays visible; longer venue information opens from its name. Mobile preserves one reading column. Tradeoff: people seeking a particular film may scroll.

**B — Venue timetable.** Attention starts with location. A date selector sits above parallel venue lanes on desktop; mobile stacks the complete venue schedules.

```text
12 November
HALL A                         STUDIO B
18:00 River                    20:30 Night Bus
8 seats · Step-free            0 seats · Stairs
Captions · Book                No captions · Sold out
```

Choose a date, compare local options, then book within a lane. Venue links provide longer details. Tradeoff: stacking weakens cross-venue time comparisons.

**C — Film index with screening sheet.** Attention starts with titles; selecting one reveals its complete screening list.

```text
River       >     RIVER SCREENINGS
Night Bus   >     12 Nov · 18:00 · Hall A
                 8 seats · Step-free · Captions
                 Book
```

Desktop uses an index beside the sheet; mobile opens a full-width sheet with a labelled return action. Dates, venues, capacity, access and booking appear together after selection. Tradeoff: checking tonight’s options requires more navigation.

**Recommendation:** Proceed with A under the existing authorization. Its shared timeline makes the program feel like a running order and keeps booking decisions in one view. A and B are the closest pair: A interleaves venues chronologically; B partitions screenings by venue.

**Handoff:** Retain B and C as alternatives, not requirements. Typography and color remain open. Prototype A with long titles, sold-out and stale-capacity states, loading, empty results and booking errors. Validate phone scanning and accessibility comprehension; these sketches establish neither usability nor accessibility compliance.
