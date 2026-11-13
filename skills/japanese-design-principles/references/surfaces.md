# Applying the principles by surface

The five principles and their tests do not change by product or platform. This file says which tests bite hardest on each kind of screen and what "enough" tends to mean there. Use it alongside the five references, never instead of them.

Every number here is a *(default)*; a project's design system overrides it.

## Viewports and input

| Situation | What changes |
| --- | --- |
| **Phone (touch, ~390 px wide)** | MA-5 is the hardest test: the job and its primary action must fit without scrolling. Touch targets 44 px; use hit areas larger than the drawn shape to keep spacing rhythm. Side gutters 16 px. |
| **Tablet** | Treat as phone width in one column or desktop width in two; never stretch a phone layout. Keep reading text to 45 to 75 characters per line (MA-3). |
| **Desktop (pointer, ~1280 px wide)** | Gutters 24 px or more. MA-3's reading measure matters most: cap text width instead of filling the screen. Pointer-only targets may be 24 px (floor 2). Keyboard flow and focus order are scored for real (floor 3). |
| **Responsive web** | Score the narrowest and the widest viewport; the layout between them follows from the same scale. |
| **Native app** | A platform pattern (system tab bar, native sheet, platform back gesture) passes where a test names it; do not rebuild a platform control to look different. |

## Kinds of screen

**Forms, onboarding, settings, checkout.** Hardest tests: TS-6 (defaults over questions), TS-5 (few choices), KA-8 (shortest path), TS-1 (one primary action). Ask only what the system cannot know; preselect the likeliest answer; one question per step only when each step is a real decision. Settings group with space (MA-6), not boxes. Validation errors follow WS-4: what happened and what to do.

**Dashboards, tables, feeds.** Hardest tests: TS-4 (numbers per row or card), SH-3 (one loud element), SH-1 and SH-2 (colour restraint), MA-6 (dividers only where a long list of same-shape rows needs them), WS-3 (age of data), SH-7 (tabular figures). Resist the "KPI tile for every number the API returns": keep the number each decision uses. Detail sits one tap away on the element it explains.

**Content and reading screens (articles, docs, detail pages).** Hardest tests: MA-3 (measure and line height), KA-4 (type styles), TS-3 (word budget applies to chrome and explanations, not to the content itself), WS-7 (content keeps its shape). Chrome stays neutral so the content is the loud element (SH-3).

**Search, lists and pickers.** Lists of content are not choices (TS-5). Hardest tests: WS-1 (longest real name, zero results), WS-6 (fallbacks for missing images), WS-7 (clamps and ways to read the full text), MA-8 (loading holds layout).

**Navigation and shells.** Hardest tests: TS-5 (at most 5 primary destinations), SH-5 (badges only where the user must act), SH-3 (persistent chrome never competes with the page), KA-5 (icon plus label is the platform pattern and passes).

**Modals, sheets and dialogs.** Each one is a surface with its own job and needs a justification in step 2: could the content live on the screen, or the action run with Undo (KA-8)? Focus moves in and returns on close (floor 3); the primary action is still exactly one (TS-1).

## States every screen must design

These are screens, not leftovers (WS-1). For each one, specify and render it:

| State | Holds | Tests that bite |
| --- | --- | --- |
| **Empty** | One sentence and one way forward. | KA-1 (no decorative illustration), TS-1, TS-3 |
| **Loading** | The populated layout's size; an indicator only after 300 ms. | MA-8 |
| **Error** | What happened and what to do, in at most 2 plain sentences. | WS-4, SH-4 |
| **Offline or stale** | The last known data with its age. | WS-3 |
| **Worst case** | Longest real name, zero, a huge number, a loss, missing image. | WS-1, WS-6, WS-7 |
| **Populated** | Realistic data, not demo data that flatters the layout. | All |

## Copy-only work

When the task is only UI strings (button labels, error messages, empty states, notifications), run all five steps on the strings. Hardest tests: KA-6 (no filler, verb buttons), SH-4 (quiet voice), TS-3 (word budget), WS-4 (honest errors), WS-3 (time stated as a fact, "Ends Fri 22:00", not as pressure).

## Reviewing a whole flow

Score each screen on its own, then add one check across the flow: the number of steps to the main task (KA-8), and the number of earned celebrations (at most 2 per flow, see tensions.md). A flow fails if any screen in it fails.
