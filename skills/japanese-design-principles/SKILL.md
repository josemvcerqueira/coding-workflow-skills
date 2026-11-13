---
name: japanese-design-principles
description: Japanese design principles (Ma, Kanso, Wabi-Sabi, Taru o Shiru, Shibui), every screen scored 5/5. Use when building a screen, component or flow; reviewing or scoring a UI; adding or removing an element; writing UI copy; or answering "should we add X?"
---

# Japanese design principles

Every element on a screen must earn its place. This skill decides what earns it. Craft, motion and edge-case data belong to sibling skills, named at the end.

The five principles, used as leading words in every file here:

- **Ma** (間, negative space): deliberate space and pauses that give shape to what surrounds them.
- **Kanso** (簡素, simplicity): no ornament; the honest, useful object shows.
- **Wabi-Sabi** (侘寂, imperfection and impermanence): honest about real data, time and bad news; never fake perfection.
- **Taru o Shiru** (足るを知る, knowing enough): exactly what the next decision needs, no more.
- **Shibui** (渋い, understated elegance): quiet on the surface, depth for the one who looks longer.

Numbers marked *(default)* in the references are this skill's defaults. A project's design system overrides one only where it states its own value.

## The pass bar

A screen passes when all five principles PASS in the same scoring round: 5/5.

- A principle PASSES only when every one of its tests PASSES with cited evidence.
- One FAIL fails the principle. One failed principle fails the screen.
- No partial credit, no averaging, no rounding up. A test without evidence is a FAIL.
- A test whose subject is absent (no motion, no money action) PASSES with the evidence "none present", after a search that proves it.
- A **screen** is one view in every state it can reach: populated with realistic data, empty, loading, error, and worst case. Score screens one at a time.

## Floors

Floors sit under all five principles. No principle may trade them away, and a floor breach fails the screen on its own.

1. **Legibility and contrast:** body text at least 16 px, no text under 12 px; contrast at least 4.5:1 for text, 3:1 for large text (24 px, or 19 px bold) and for control edges and icons.
2. **Tap targets:** at least 44 x 44 px, with at least 8 px between neighbouring targets.
3. **Keyboard and screen reader:** every control is reachable and works by keyboard, shows a visible focus ring, and has an accessible name that says what it does.
4. **Reduced motion:** under `prefers-reduced-motion`, movement is replaced by a fade or an instant change, and no information lives only in motion.
5. **Money-moving actions:** before money moves, one plain sentence states the amount, the direction and the worst case; then either an Undo window (a visible countdown) or an explicit confirm.

## Modes

- **Build:** write the screen's one job in one sentence ("let a person call Up or Down on one event in one tap"). Start from an empty screen holding only that job's content and its primary action. Every further element enters only through step 2. Then run steps 3 to 5 on what you built.
- **Review:** run steps 1 to 5 on the existing screen.
- **"Should we add X?":** run step 2 on X first: name its job, and name the element that already does that job or that X could replace. Answer yes only when the screen still scores 5/5 with X, and say what X replaces.
- **UI copy:** strings are elements. Run all five steps; every reference has a copy layer.

## Steps

### 1. Inventory

List every element in every state: each text string, icon, image, control, divider, border, shadow, colour, motion and number.
**Done when** every visible element in every state is listed. For code, every rendered node is accounted for; for a rendered page, every element in the screenshots.

### 2. Justify

For each element, write the one job it does for this user right now. Mark **cut** an element with no job; mark **merge** an element whose job another element already does.
**Done when** every element has a job no other element does, or is marked cut or merge.

### 3. Test

Open all five references and run every test in each:
[ma.md](references/ma.md), [kanso.md](references/kanso.md), [wabi-sabi.md](references/wabi-sabi.md), [taru-o-shiru.md](references/taru-o-shiru.md), [shibui.md](references/shibui.md).
Record each test as `ID PASS|FAIL evidence`, where evidence names the element, the value and the file and line or the screenshot. When two principles pull against each other or against a floor, read [references/tensions.md](references/tensions.md) before choosing a fix; read it at least once per run.
**Done when** every test of all five references is answered with evidence and every floor is checked.

### 4. Fix

Fix in this order: remove, then merge, then restyle, and add last. Every addition names the element it replaces or the test it makes pass. After each fix round, rescore all five principles, because a fix for one often breaks another.
**Done when** all five principles PASS in the same round and no floor is breached.

### 5. Verify on the rendered screen

When the UI can render, take screenshots at phone width (390 x 844) and, when the UI ships on desktop, at 1280 x 800, with the agent-browser skill, in every state. Score from what the screenshots show; the code only explains why. When nothing can render yet (a spec or a sketch), say so on the scorecard.
**Done when** the scorecard cites at least one observation from the rendered screen at each width, or states that no render exists.

### Stuck loop

After 3 fix rounds with a FAIL that only a product or taste decision can clear, stop. Put exactly that one decision to the owner: the two options, what each costs in principles, and your recommendation. Decide yourself whenever one option is clearly better.

## Scorecard

One scorecard per screen. Keep the full test log from step 3 beside it; the scorecard shows only the deciding line.

```
Screen: Home feed card · states: populated, empty, error, worst case · rendered 390 / 1280
| Principle     | Result | Deciding evidence                                        |
| Ma            | PASS   | gaps 8 / 24 / 48 on scale; buttons clear by 32 px (MA-4) |
| Kanso         | FAIL   | KA-3: gradient on card header, no state carried          |
| Wabi-Sabi     | PASS   | loss row same size as win row (WS-2), screenshot 390     |
| Taru o Shiru  | PASS   | 34 words of explanatory copy (TS-3)                      |
| Shibui        | PASS   | one accent, 6% saturated area (SH-2)                     |
Floors: all met · Result: FAIL (4/5)
Cut: "Trending now" label (heading repeated the tab) · Merged: price + change into one line
```

## Who does what

- **Sonnet** does the mechanical work: the inventory, the screenshots, and collecting the measurements each test asks for (spacing values, word counts, colours, contrast ratios).
- **Opus** builds and fixes the UI. Opus also runs the scoring audit as a fresh subagent that receives only the screenshots, the code paths and this skill, never the builder's reasoning: an agent that built a screen flatters it.
- **Fable** only reviews contested audit findings or a whole new product flow.
- The agent that fixes is never the agent that signs off. Sign-off is a 5/5 scorecard from a fresh auditor.

## Sibling skills

This skill decides what stays. For how it is made, use: `emil-design-eng` for polish and component craft; `animate` and `apple-design` for motion; `break-ui` for worst-case data (WS-1); `mobile-native` for phone platform fixes; `agent-browser` for screenshots.
