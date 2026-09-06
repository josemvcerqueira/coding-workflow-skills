# Workflow Dashboard

Standalone localhost dashboard for active coding-workflow runs. The first view shows what is running, whether it is healthy and on schedule, which runtime model is actually observed, exact available token use, and which tickets can start when the current work finishes. Detailed records remain in the read-only API. The Bun server, browser page, and telemetry worker live here so installing `coordinate-work` copies instructions only. Runtime requirements are Bun 1.3 or newer and Python 3.10 or newer.

## Install

```sh
cd apps/workflow-dashboard
npm pack
bun install --global ./coding-workflow-dashboard-0.1.3.tgz
```

This installs a self-contained package outside the repository and exposes `workflow-dashboard` through Bun's global executable directory. Keep that directory on `PATH` for coordinator processes. After this package is published, `bun install --global coding-workflow-dashboard` is the equivalent release install.

For source-linked development, use `bun link` from this directory instead.

## Commands

```sh
workflow-dashboard heartbeat WORKFLOW --agent-path PATH --parent PATH \
  --role ROLE --stage STAGE --state STATE --summary TEXT --next-action TEXT \
  --stage-started-at ISO_TIME --expected-duration-seconds SECONDS \
  --estimate-set-at ISO_TIME --runtime-provider PROVIDER --requested-model MODEL
workflow-dashboard pulse WORKFLOW --agent-path PATH
workflow-dashboard snapshot WORKFLOW
workflow-dashboard serve WORKFLOW
```

`pulse` refreshes a coordinator's `heartbeat_at` without changing its last progress milestone, summary, or next action. The dashboard therefore distinguishes recent liveness (`quiet`) from recent progress (`healthy`).

Workers use `completed` after a successful stage handoff and cleanup. `stopped` means the runtime ended before a successful handoff, while `paused` means the workflow intentionally paused with a durable checkpoint. The dashboard recognizes older stopped implementation records as expected history after their ticket advances to review or beyond.

The coordinator sets an explicit expected duration for each assigned stage. Historical tickets may later suggest a starting value, but the coordinator-confirmed estimate is authoritative. A resumed stage gets a new `stage_started_at`, estimate, and `estimate_set_at`; assignment-level `started_at` remains unchanged.

Codex telemetry is discovered under `~/.codex/sessions` by default. Claude telemetry is discovered under `~/.claude/projects`; override or add roots with repeatable `--sessions-root` and `--claude-sessions-root` options. Model identity is labeled observed only when the runtime transcript reports it. Requested model intent remains visibly distinct.

When a runtime reports both latest input and its context-window size, the page shows occupancy plus the compact used/window values. When Claude reports exact token counts without a window size, the page still shows latest input and cumulative session processing, but never invents a percentage. Session totals include reported cached-input processing and are labeled separately from current context.

The dashboard is optional. Coordination continues using its canonical Markdown and JSON records when this command is unavailable.

## Upgrade from the former bundled dashboard

Keep an installed legacy `coordinate-work/assets` or `coordinate-work/scripts` directory unchanged while a recorded server still uses it. The owning coordinator checkpoints, verifies the recorded PID and start identity, stops that server and its worker, confirms both exited, installs this package, and only then replaces the skill installation. If the run remains active, start `workflow-dashboard serve` and record its new process tuple. Never delete a live legacy server's files in place.

## Test

```sh
bun run test
```
