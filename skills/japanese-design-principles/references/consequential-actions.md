# Consequential actions

Floor 5 in SKILL.md. It applies only where an action is costly or hard to reverse. Where the screen has none, the evidence is "none present", after a search that proves it.

## What counts

An action is consequential when a wrong tap costs the user something they cannot get back for free:

- **Money moves:** pay, buy, transfer, subscribe, tip, stake.
- **Data is destroyed:** delete, overwrite, reset, remove a member, revoke access.
- **Something goes out:** send, post, publish, share, invite, notify other people.
- **Something is locked in:** submit a final form, cancel a contract, change a plan.

The project decides the edge cases (see Project specifics in SKILL.md). When unsure, ask one question: can the user fully undo this in under a minute without help? If not, it is consequential.

## What the floor requires

1. **One plain sentence before it happens**, stating what the action does and the worst case: the amount and direction for money, what is lost for a delete, who sees it for a send. At most 20 words *(default)*.
2. **Then one of two safety nets:**
   - **Undo window:** the action is held for a visible countdown (3 s *(default)*) and can be cancelled. Use this whenever the action can wait a few seconds.
   - **Explicit confirm:** one confirm control that names the action ("Delete 3 files"), used only where the action cannot be held (it takes effect at once, or it reaches other people).

The sentence sits next to the control that triggers the action, not on a separate screen.

## Sentence pattern

State the thing, then the worst case, in plain words:

- "$20 charged to Visa 4242. Refundable within 14 days."
- "Deletes 3 files. They stay in Trash for 30 days."
- "Sends to 240 people. You cannot recall it."
- "Cancels your plan on 1 March. You keep access until then."

## How this meets the principles

- **Kanso:** an Undo window replaces a confirm dialog and counts as a win (KA-8). The sentence is exempt from KA-6's button rule and TS-3's word budget, and stays short.
- **Taru o Shiru:** the cost of an action is part of "enough to act safely" (TS-8). Never cut it to save space.
- **Wabi-Sabi:** state the real worst case, not a reassuring one (WS-5).
- **Shibui:** the sentence is calm and factual; no red banners or exclamation marks (SH-4).
- **Ma:** the Undo countdown is a designed pause with a job (MA-7).

## Common failures

1. "Are you sure?" with no information. Fix: say what happens and what it costs.
2. A confirm dialog after every action, including reversible ones. Fix: act, then offer Undo.
3. An Undo that vanishes in 1 s or hides behind a gesture. Fix: visible countdown, at least 3 s, reachable by keyboard.
4. A cost shown only after the tap. Fix: show it on the control before.
5. A destructive control styled like the primary action and placed next to a harmless one. Fix: separate them (MA-4) and name the destructive one by its effect.
