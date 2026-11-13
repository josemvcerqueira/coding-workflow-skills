# Kanso (簡素): simplicity

Kanso is one of the principles of Zen-influenced Japanese aesthetics: plainness that comes from leaving things out, so the honest form and use of an object show.

## The idea for a screen

Kanso asks of each element: is this the plainest form that still does the job? It works on **how** things look and **how** they are reached: no ornament, no effects, no extra styles, no filler words, no extra step. (How **many** things a screen holds is Taru o Shiru's question.) A Kanso screen looks like it could not be made plainer without losing its use.

## Across layers

| Layer | What Kanso asks |
| --- | --- |
| Layout | One container level where one is enough; no boxes for show. |
| Type | Few sizes, few weights, one family. Hierarchy from size and space, not from styles piled up. |
| Colour | Flat fills. No gradient, glow or texture that carries no state. |
| Copy | The fewest words that say it; verbs on buttons; no filler. |
| Motion | Motion only as the visible result of a cause. |
| States | One sentence and one action in an empty or error state, not an illustration plus three links. |
| Data | Numbers in their plainest true form: "$10.60", not "$10.60 USD ▲ (+6.00%)". |
| Interaction | The fewest steps the floors allow. Undo instead of a confirm screen where the action can be reversed. |

## Tests

**KA-1 No decoration.** PASS when no element in the step 2 table has "looks nice" or "fills space" as its only job: no ornamental icons, background shapes, decorative illustrations on working screens, or flourishes. Evidence: the step 2 rows checked, and any decoration found.

**KA-2 One surface treatment.** PASS when each surface uses at most one of: a fill change, a border, a shadow; and boxed containers nest at most 2 deep (a card in a page, never a card in a card in a panel). Evidence: each surface with its treatment; the deepest nesting.

**KA-3 No ornamental effects.** PASS when the screen has zero gradients, glows, blur or glass, textures, text shadows or faux-3D, except where the effect carries a state (focus, elevation of an open sheet) or is the content itself (a photo). A brand moment follows [tensions.md](tensions.md). Evidence: effects found in CSS and screenshots.

**KA-4 Type styles.** PASS when a screen uses at most 4 font sizes, at most 2 weights and one family *(defaults)*; a second family is allowed only for tabular or monospaced numbers. Evidence: the sizes, weights and families found.

**KA-5 Icons earn their place.** PASS when every icon either replaces a word or stands for a widely known action (search, close, share), no icon sits beside a label that says the same thing (a tab bar's icon plus label is the platform pattern and passes), and each icon means one thing across the app. Evidence: each icon and its job.

**KA-6 Copy without filler.** PASS when UI copy contains none of: "please", "simply", "just", "easily", "successfully", "in order to", "click here", "Are you sure?"; and every button label is a verb or verb plus object of at most 3 words *(default)*. Evidence: strings checked, with any hits.

**KA-7 Motion has a cause.** PASS when every animation runs because of a user action or a change in data or state; zero entrance animations for show, parallax or idle motion. Evidence: each animation and its trigger.

**KA-8 Shortest path.** PASS when the screen's main task takes no step the floors do not require: no intermediate screen, modal, wizard step or confirm dialog where an Undo window would meet the money floor. Evidence: the tap count for the main task and each step's reason.

## Common failures, ranked

1. Card, border, shadow and tinted fill all on one element. Fix: keep one; usually the fill or the shadow.
2. Six text styles on one screen (caps label, bold title, subtitle, body, caption, footnote). Fix: merge to 3 or 4 sizes and 2 weights.
3. A confirm dialog after every action. Fix: act at once and offer Undo, keeping the floor's plain sentence.
4. Icons on every label and every heading. Fix: delete icons that repeat their label.
5. Filler copy: "Your changes have been saved successfully!". Fix: "Saved".
6. Gradient headers and glowing buttons. Fix: flat fills; one accent colour for the action.
7. Decorative illustrations on empty states. Fix: one sentence and one action.
8. Entrance animations on every list item. Fix: render in place; animate only what changed.

## Before and after

**Trade card.** Before: a glass card with a gradient border, a glowing "BUY NOW 🚀" button and a confirm modal ("Are you sure you want to buy?"). After: a flat card, a plain "▲ Up" button, and a 3 s Undo window with one sentence. Same safety, one step fewer, no ornament.

**Settings row.** Before: gear icon, "Notification Preferences" label, a chevron, a help icon and a caption under it. After: "Notifications" and the current value; the row itself opens the detail.

**Empty state.** Before: an illustration, "Nothing here yet!", a paragraph and three buttons. After: "No calls yet." and one button that opens the feed.

## The misreading

Kanso is not bare or cold, and it never cuts what makes the object usable or safe. The amount, direction and worst case of a money action stay (the money floor); a label that a person needs to understand an icon stays. Kanso removes ornament, effects, steps and filler; Taru o Shiru decides how much content is enough.
