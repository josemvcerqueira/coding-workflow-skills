# Shibui (渋い): understated elegance

Shibui first described an astringent taste, like an unripe persimmon, and came to mean refined, quiet taste that grows on you.

## The idea for a screen

A Shibui screen does not shout. It has one loud thing, a calm palette, a quiet voice, and nothing that begs for a tap. Its quality shows on the second look: numbers that do not jitter, corners that nest, punctuation that is right. Brand and joy appear in a few earned moments, tied to what the user did, and then step back.

## Across layers

| Layer | What Shibui asks |
| --- | --- |
| Layout | One element at the top of the hierarchy; everything else clearly below it. |
| Type | Weight and size changes small and few; no all-caps shouting. |
| Colour | Neutrals carry the screen; one accent marks the action; semantic colours only where they mean something. |
| Copy | Calm, factual voice. Real deadlines stated as facts, never as pressure. |
| Motion | Small amplitude; celebration short, rare and earned. |
| States | Success is quiet ("Saved"); failure is calm (see Wabi-Sabi). |
| Data | Numbers set in tabular figures so changes do not jump. |
| Interaction | No badge, dot or pulse unless this user must act. |

## Tests

**SH-1 One accent.** PASS when at most one accent hue marks actions on the screen, semantic colours (up and down, success and error) appear only where they carry that meaning, and every other colour is neutral. Evidence: the hues found and where each is used.

**SH-2 Saturated area.** PASS when saturated colour covers at most 10 % of the screen area *(default)*, not counting photos and video. Evidence: estimate from the screenshots, naming the largest saturated areas.

**SH-3 One loud element.** PASS when exactly one element per screen state sits at the top of the visual hierarchy (largest size or strongest contrast), and no second element competes at that level. Evidence: the loudest element and the next one down.

**SH-4 Quiet voice.** PASS when UI copy has zero exclamation marks, no all-caps run longer than 2 words, no hype words ("amazing", "huge", "don't miss", "insane", "to the moon"), and no emoji in interface chrome. User-written content is exempt. Evidence: strings checked, with any hits.

**SH-5 Nothing begs.** PASS when every badge, dot and counter marks something this user must act on, and at most one element per screen moves on its own (a live-data marker), at low amplitude. Evidence: each badge and each self-moving element with its reason.

**SH-6 Earned celebration.** PASS when every celebration (confetti, flames, a bump, a haptic) follows the user's own action or result, lasts at most 1 s *(default)*, plays once per event, and has a reduced-motion form. Evidence: each celebration and its trigger, duration and reduced-motion form.

**SH-7 Craft for the second look.** PASS when all four hold: numbers that change use tabular figures; nested corners follow outer radius = inner radius + padding; icons share one stroke weight and grid; text uses real punctuation (curly quotes, en dash for ranges, true minus "−" for negatives). Evidence: one example per item, or the failing one. For deeper polish, use `emil-design-eng`.

## Common failures, ranked

1. Three or four accent colours (blue links, purple buttons, orange badges). Fix: one accent; the rest neutral.
2. Two hero elements fighting (a big balance and a big banner). Fix: one wins; shrink or remove the other.
3. Red dots and badges on tabs for things that need nothing from the user. Fix: remove them.
4. "🔥 HUGE MOVE! Don't miss out!" Fix: "Nvidia −6% today."
5. Confetti on every tap. Fix: one short moment on a good result only.
6. Prices that jump sideways as digits change. Fix: `font-variant-numeric: tabular-nums`.
7. A saturated full-screen background. Fix: neutral surface; colour on the one action.

## Before and after

**Result screen.** Before: full-screen confetti, "YOU WON!!!" in 48 px caps, a pulsing share button, three badges. After: the card turns to "Good call +$6" at the size of the card's number, one 600 ms flourish, and a quiet share button.

**Dashboard.** Before: six KPI tiles, each a different bright colour with an icon and an arrow. After: neutral tiles; only the one metric that moved past its alert line carries the accent.

**Notification.** Before: "Hurry! Your call ends soon!!" After: "Your Benfica call ends at 22:00."

## The misreading

Shibui is not dull, grey or timid. Low contrast fails the legibility floor, and removing all personality fails the brand: Shibui keeps brand and joy, placed in a few earned moments (SH-6) instead of spread over every surface. Quiet means confident: one clear voice, not no voice.
