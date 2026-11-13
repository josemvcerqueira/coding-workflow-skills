# Taru o Shiru (足るを知る): knowing enough

The phrase comes from the Laozi ("one who knows enough is rich") and is carved on the stone basin at Ryōan-ji in Kyoto as 吾唯足知, "I only know contentment".

## The idea for a screen

Taru o Shiru asks how **many** things the screen holds: actions, choices, words, numbers, settings, features. Enough is set by the next decision the user makes on this screen, not by what the system knows or what the team built. Everything the decision needs is on the surface; everything else is one tap away or gone.

"Enough" cuts both ways. A screen that hides what a person needs to act safely has too little, and fails as surely as a cluttered one.

## Across layers

| Layer | What Taru o Shiru asks |
| --- | --- |
| Layout | One primary action. Secondary detail behind the element it explains. |
| Type | Short headings; text in small blocks under a word budget. |
| Colour | Only as many colour meanings as the decision uses; no legend to learn. |
| Copy | Each fact said once; explanations only where the user would stall without them. |
| Motion | One animation per change; no sequence the user waits through before acting. |
| States | An empty state holds one sentence and one way forward. |
| Data | Few numbers, each answering a question the user has now, at the precision they act on. |
| Interaction | Defaults instead of questions; few options per decision; one way to do each thing. |

## Tests

**TS-1 One primary action.** PASS when each screen state has exactly one element styled as primary. Two halves of one equal decision (Down and Up, No and Yes) styled at the same weight count as one primary decision. Evidence: the primary element(s) per state.

**TS-2 Each fact once.** PASS when no fact appears twice on the screen (a price in the header and on the card, a title repeated as heading and label). Encodings the floors require together (arrow plus colour plus word) count as one. Evidence: the facts listed, with any repeats.

**TS-3 Word budget.** PASS when headings have at most 6 words, any text block at most 25 words, and the explanatory copy on one phone screen (everything except user content, names and data) totals at most 40 words *(defaults)*. Evidence: the counts.

**TS-4 Numbers.** PASS when a card or row shows at most 3 numbers *(default)*, each answers a question the user has at this moment, and precision is no finer than the decision needs: money in whole cents or whole units, percentages whole above 1 %. Evidence: each number with its question.

**TS-5 Few choices.** PASS when any single decision shows at most 3 options at once *(default)*, longer sets sit behind search or a "More", and primary navigation has at most 5 destinations. Lists of content (search results, a feed) are not choices. Evidence: each decision and its option count.

**TS-6 Defaults over questions.** PASS when every input and setting has a sensible default, and the screen asks nothing the system can know or infer (from the profile, history, locale or device). Evidence: each question with why the system cannot answer it.

**TS-7 One way to do each thing.** PASS when no action has two entry points on the same screen (a header button and a floating button that both add; a row tap and a "View" link that both open). Evidence: actions and their entry points.

**TS-8 Enough to act safely.** PASS when, for every action on the surface, the user can see what it does and what it costs before acting, without a tap into detail. Evidence: each action and where its effect and cost show.

## Common failures, ranked

1. Paragraphs of explanation on working screens. Fix: one line; the rest behind "Why?" on the element, or gone.
2. Several filled buttons competing. Fix: one primary; the others become text buttons or move into the element they act on.
3. Every number the API returns (open, high, low, volume, market cap). Fix: keep the one number the decision uses.
4. Settings for things the system can decide. Fix: pick the default; offer the change only where real users need different values.
5. The same fact in two places. Fix: keep it where the decision is made.
6. Two ways to do the same thing. Fix: keep the one closest to the content.
7. Cutting the cost of an action to save space. Fix: restore it; TS-8 and the money floor outrank the word budget.

## Before and after

**Trade card.** Before: price, change, 24 h high, low, volume, a chart, entry, exit and leverage fields, three buttons. After: one number (the price or the chance), when it ends, and two buttons; the system sets entry, exit and size and states the limits in the Undo window before money moves.

**Feed header.** Before: "Trending Markets Today: discover what the community is predicting right now" above a feed. After: no header; the feed is the page.

**Onboarding.** Before: twelve questions on one form. After: four questions as single-tap cards, two of them skippable, each with a preset answer.

## The misreading

Taru o Shiru is not minimalism for its own sake and not starvation. "Enough" is measured against the user's next decision: cutting the worst case from a money action, or the label that makes an icon readable, fails TS-8. It also does not mean "keep everything and hide it in menus": detail that no user decision needs is cut, not buried.
