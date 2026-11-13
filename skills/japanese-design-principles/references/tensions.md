# Tensions

The five principles sometimes pull against each other or against a floor. A 5/5 design always exists that satisfies both sides; the rules below say which fix to try first. When none works after 3 rounds, follow the stuck loop in SKILL.md.

## Floors win every tension

The floors are defined in SKILL.md: legibility and contrast, target size, keyboard and screen-reader access, reduced motion, and a clear statement plus Undo or confirm for consequential actions. No principle may trade any of them away. When a principle's test and a floor disagree, keep the floor and redesign until the principle's test passes too.

## The general order

When two fixes both work, prefer the one earlier in this list:

1. Remove an element (and its space, words and colour with it).
2. Merge two elements into one.
3. Move detail one tap away, onto the element it explains.
4. Restyle.
5. Add, naming what the addition replaces.

## Ma vs Taru o Shiru

Space wants room; the content the decision needs wants room too.
**Rule:** cut content first (TS-2 to TS-5), then move secondary detail one tap away (TS-8 still holds). Spacing stays on the scale and keeps its 2x rhythm (MA-2). If the job still does not fit at the smallest supported viewport (MA-5), the screen does two jobs: split it.

## Ma vs target size

44 px touch targets and 8 px between them eat space on small screens.
**Rule:** the target floor wins. Make the hit area larger than the drawn shape (padding or an invisible hit area), so visual spacing keeps its rhythm.

## Kanso vs clear consequential actions

Kanso wants fewer words and steps; a costly or hard-to-reverse action needs its effect and worst case stated.
**Rule:** the floor-5 sentence is exempt from KA-6's button rule and TS-3's word budget, but it stays one short statement, at most 20 words *(default)*, in plain words: "$20 charged to Visa 4242. Refundable within 14 days." An Undo window that meets the floor replaces a confirm screen and counts as a Kanso win (KA-8). A confirm dialog is used only where the action cannot be held for a window. See [consequential-actions.md](consequential-actions.md).

## Kanso vs redundant encoding

Accessibility needs meaning carried in more than colour (arrow plus colour plus word); Kanso and TS-2 dislike repeats.
**Rule:** encodings the floors require for one fact count as one element and one fact. Extra encodings beyond the floor (an icon, a caption and a tooltip all saying "up") are cut.

## Wabi-Sabi vs accessibility

Muted, natural, uneven looks tempt low contrast, thin type and irregular alignment.
**Rule:** Wabi-Sabi applies to the truth of the content, never to contrast, size or alignment. Floors and WS-8 hold; honesty about data, time and failure is where Wabi-Sabi lives.

## Wabi-Sabi vs Kanso and Taru o Shiru

Cutting can quietly remove bad news (the loss row, the stale mark, the error detail).
**Rule:** bad news, age and errors are never the element cut to meet a budget. Cut something else, or merge the bad news into the element it qualifies ("$10.60 · as of 14:02").

## Wabi-Sabi vs Shibui

An honest loss in semantic red can look loud.
**Rule:** losses and gains share one size and one colour strength (WS-2). Calm comes from treating both the same, never from shrinking the loss.

## Shibui vs brand fun

A playful brand wants presence; Shibui wants quiet.
**Rule:** brand fun lives in at most 2 earned moments per flow *(default)*, each tied to a user action or result, at most 1 s, with a reduced-motion form (SH-6). Persistent chrome (headers, tab bars, backgrounds) stays neutral. Brand colour may be the one accent (SH-1).

## Shibui vs Taru o Shiru on depth

Shibui wants depth for the one who looks longer; Taru o Shiru wants a lean surface.
**Rule:** both pass when depth sits one tap away on the element it explains (a tap on the number opens its history chart) and the surface stays within its budgets. Depth never means more on the surface.

## Ma vs Shibui on hierarchy

A large clear field around the primary action can make it the loudest element even when the content should be.
**Rule:** decide the one loud element first (SH-3), usually the content on a feed and the action on a form; Ma's clear field (MA-4) serves that choice.
