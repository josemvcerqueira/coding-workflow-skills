---
name: setup-project-context
description: Use when the user explicitly invokes the former setup-project-context name to set up or refresh coding workflow context.
license: MIT
disable-model-invocation: true
---

# Set up project context

This is the compatibility entrypoint for [setup-workflow](../setup-workflow/SKILL.md). Read that skill and its required references, then perform the requested setup or refresh through its external workspace contract. Keep the user's selected project and existing decisions.

Locate this collection's installed setup-workflow companion if the sibling path is absent. If unavailable, report the missing dependency; do not install it silently or fall back to creating context inside the product repository. Reading the companion is part of this explicit invocation, not implicit skill selection.

The new entrypoint sets up external directories and context. It preserves read-only exploration, focused subagents for larger projects, one parent writer, no application startup, and explicit-only invocation. A setup request never deletes specs or starts implementation.
