# Wabi-Sabi (侘寂): imperfection and impermanence

Wabi-Sabi grew up around the Japanese tea ceremony: beauty in what is plain, worn and passing, and contentment with things as they are.

## The idea for a screen

A Wabi-Sabi screen tells the truth about its data, its time and its failures. Real names are long or short, prices are old after a minute, calls are missed, images fail to load. The screen shows these as they are, calmly, at the same weight as good news, and it never stages a perfect world: no fake counts, no fake urgency, no demo data hiding the hard cases.

Impermanence on a screen means time is visible: things have an age and an end.

## Across layers

| Layer | What Wabi-Sabi asks |
| --- | --- |
| Layout | Content keeps its natural shape; the layout follows real content, not an ideal grid. |
| Type | Real text at real length, wrapped, not cut to keep tiles even. |
| Colour | Bad news in its semantic colour at the same strength as good news. |
| Copy | Plain truth: "Missed", "Lost $5", "Prices are 2 minutes old". |
| Motion | Change shown as it happens; no motion that suggests progress that is not happening. |
| States | Empty, loading, error and stale are designed screens, not leftovers. |
| Data | Real numbers, honest rounding, visible age. |
| Interaction | What happened is always findable: a missed call, a failed payment, an expired code. |

## Tests

**WS-1 Scored with real data in every state.** PASS when the screen is scored with realistic data in each state it can reach: populated, empty, loading, error, and a worst case (longest real name, a loss, zero, a huge number). Each state is rendered or, before code exists, specified. Evidence: the states and the data used. For the worst-case set, use the `break-ui` skill.

**WS-2 Bad news at equal weight.** PASS when losses, misses, errors and negative numbers use the same size, weight and position as their good counterparts, carry a visible minus sign ("−$5") or a plain word ("Missed"), and are never greyed out, shrunk or moved lower. Evidence: a good and a bad row side by side.

**WS-3 Time is visible.** PASS when time-bound content shows its age or its end ("2h ago", "Ends Fri"), and data older than its freshness window shows an "as of" time or a stale mark. Freshness windows *(defaults)*: live prices 30 s, other data 5 min. Evidence: each time-bound item and its label.

**WS-4 Honest errors.** PASS when every error state says in at most 2 plain sentences what happened and what to do next; no "Oops", no bare "Something went wrong", no blame on the user; and no spinner runs past 10 s without words. Evidence: each error string and the long-wait behaviour.

**WS-5 Nothing fake.** PASS when every number and claim comes from real data: no invented urgency ("Only 2 left!"), no fake counters, no made-up social proof, no stock-photo people presented as users, no progress bar that does not track real progress. Evidence: the source of each number and claim.

**WS-6 Designed fallbacks.** PASS when every image, avatar and remote value has a designed fallback (an initial in a circle, a neutral tile, a dash), so missing data looks intended. Evidence: each remote item and its fallback, ideally a screenshot with images blocked.

**WS-7 Content keeps its shape.** PASS when text wraps to its natural length up to a stated clamp (titles 2 lines *(default)*) and truncation always leaves a way to read the full text. Uneven heights that follow real content are kept. Evidence: the clamp values and a worst-case screenshot.

**WS-8 The craft stays exact.** PASS when the rendered screen shows no misaligned edges, clipped text, broken images, overlapping elements or layout shift. Evidence: screenshots at both widths.

## Common failures, ranked

1. Reviewed only with demo data that flatters the design. Fix: render the worst case and every state (WS-1).
2. Losses in small grey text while wins are big and green. Fix: same size and place; red with a minus sign.
3. A live price with no age, frozen when the feed drops. Fix: show "as of 14:02" past the freshness window.
4. "Oops! Something went wrong." Fix: "Payment failed: your card was declined. Try another card."
5. Fake scarcity or fake activity ("12 people are looking at this"). Fix: delete it, or show the true number.
6. Broken image icons. Fix: a neutral tile or an initial.
7. Titles cut to one line with an ellipsis to keep a grid even. Fix: allow 2 lines; let rows differ in height.

## Before and after

**Portfolio list.** Before: winning calls in large green type at the top; losing calls collapsed under "Show more" in grey. After: every call in one list by time, "✓ Good call +$6" and "✕ Missed −$5" in the same size, each in its semantic colour.

**Feed card when the price feed stalls.** Before: the last price keeps showing as if live. After: the price keeps its size and gains "as of 14:02", and the buttons say "Waiting for a fresh price" until the feed returns.

**Profile with no photo.** Before: a broken image and an empty grey box. After: a coloured circle with the person's initial, the same size as a photo.

## The misreading

Wabi-Sabi is honest and calm, never sloppy or broken. The imperfection lives in the content (real names, real losses, real age), never in the craft: misalignment, grunge textures, fake hand-drawn fonts and visible bugs fail WS-8. Showing bad news honestly also means showing it plainly, without drama: no alarm banners for an ordinary loss.
