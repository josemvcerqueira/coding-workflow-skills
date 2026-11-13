# Ma (間): negative space

Ma names the interval between things, in space and in time. Japanese architecture, music and theatre use it; Arata Isozaki's 1978 exhibition "Ma: Space-Time in Japan" brought the word to Western designers.

## The idea for a screen

Space is a material you place on purpose. It groups what belongs together, separates what does not, and tells the eye where to rest and where to act. Space laid out with Ma has **rhythm**: small gaps inside a group, large gaps between groups, and a clear field around the one thing that matters. A screen with one gap size everywhere has space but no Ma.

Time has Ma too: the pause before a loader appears, the seconds an Undo stays open, the short beat of a transition. A pause is designed, never accidental.

## Across layers

| Layer | What Ma asks |
| --- | --- |
| Layout | Groups separated by space before lines or boxes. Gaps from one scale. |
| Type | Line height that lets lines breathe; line length the eye can track. |
| Colour | Flat neutral background, so space reads as space, not as a pattern. |
| Copy | Short blocks with space between them, rather than one long paragraph. |
| Motion | Durations from a short set; one thing moves at a time inside a group. |
| States | Empty and loading states keep the populated layout's spacing, so nothing jumps. |
| Data | Numbers in a row get room to be read one at a time. |
| Interaction | Clear space around targets; a visible pause before a consequential action commits. |

## Tests

**MA-1 Spacing scale.** PASS when every margin, padding and gap value is on the scale 4, 8, 12, 16, 24, 32, 48, 64, 96 px *(default)*. Exempt: 1 px hairlines and platform values such as safe-area insets. Evidence: the off-scale values found, or "none" with the files searched.

**MA-2 Rhythm.** PASS when the gap between groups is at least 2x the gap inside those groups (8 inside, 24 between), and the screen uses at least three steps of the scale. Evidence: the inner and outer gap for each group.

**MA-3 Gutters and reading measure.** PASS when side gutters are at least 16 px at phone width and 24 px at desktop width, reading text runs 45 to 75 characters per line at desktop, and body line height is 1.4 to 1.6 *(defaults)*. Evidence: measured values.

**MA-4 Clear field around the primary action.** PASS when no unrelated element sits within 24 px of the primary action *(default)*. Two halves of one decision (Yes and No, Cancel and Save) may sit 8 to 16 px apart, so they read as a pair. Evidence: the nearest unrelated element and its distance.

**MA-5 The job stays in view.** PASS when, at the smallest supported viewport (390 x 844 for a phone *(default)*), the screen's main content and its primary action are fully visible without scrolling. Evidence: screenshot at that size.

**MA-6 Space separates first.** PASS when every divider line and every bordered box sits where space alone cannot separate (a long list of same-shape rows, a table). Evidence: each divider or box with the reason space fails there, or "none".

**MA-7 Motion durations.** PASS when every UI transition takes 150, 200 or 300 ms *(default set)*, and any longer duration is a named window with a job (a 3 s Undo countdown). Evidence: durations found in code. For curves and springs, use the `animate` skill.

**MA-8 Waiting has shape.** PASS when a loading indicator appears only after 300 ms of waiting, a loading state holds the populated layout's size (no layout shift), and a transient message stays at least 4 s or until dismissed. Evidence: timings in code and the loading screenshot.

## Common failures, ranked

1. One gap size everywhere (16 px between everything). Fix: 8 inside groups, 24 or 32 between them.
2. Dividers between every row and every section. Fix: delete them and widen the gap between groups.
3. A card inside a card inside a panel, each with its own padding. Fix: one container; the rest is spacing.
4. Off-scale values (13 px, 18 px, 22 px) from eyeballing. Fix: snap to the nearest scale step.
5. The primary action crowded by secondary links. Fix: move secondary links away or behind the element they belong to.
6. A spinner that flashes for 80 ms on every fast load. Fix: wait 300 ms before showing it.
7. A huge hero that pushes the action below the fold. Fix: cut the hero height until the job fits at the smallest supported viewport.

## Before and after

**Product card.** Before: image, title, price, rating, stock note and two buttons stacked with 12 px between all of them, divider lines between each. After: image, then title and price grouped at 8 px, a 32 px gap, then the two buttons 12 px apart, 24 px clear of anything else. Same content minus the stock note; the eye now lands on the buttons.

**Settings page.** Before: 14 rows, each in its own bordered box, 16 px apart. After: three groups of rows with 8 px inside and 32 px between, one group heading each, no boxes. The page looks shorter though it holds the same rows.

**Error toast.** Before: a red toast that slides in and out in 1.5 s. After: it stays until dismissed or 6 s, and the screen behind keeps its layout.

## The misreading

Ma is deliberate rhythm, never emptiness for its own sake. A screen that is half blank, with the action pushed off-screen or small text floating in a void, fails MA-5 and MA-2 just as a crowded one fails MA-4. Add space by removing things (Taru o Shiru, Kanso), never by shrinking what remains below the floors.
