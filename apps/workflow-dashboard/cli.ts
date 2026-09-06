#!/usr/bin/env bun

import { fileURLToPath } from "node:url";

const [command, ...args] = Bun.argv.slice(2);

const SERVE_OPTIONS = new Set([
  "--host",
  "--port",
  "--sessions-root",
  "--claude-sessions-root",
  "--capacity",
  "--refresh-ms",
  "--stale-after",
  "--asset",
  "--worker-script",
]);

function serveHelp() {
  return `Usage: workflow-dashboard serve WORKFLOW [options]

Options:
  --host HOST              Loopback host (must be 127.0.0.1)
  --port PORT              Port, or 0 for an available port
  --sessions-root PATH     Codex sessions root; repeatable
  --claude-sessions-root PATH
                           Claude projects root; repeatable
  --capacity COUNT         Runtime capacity shown by the dashboard
  --refresh-ms MS          Snapshot refresh interval
  --stale-after SECONDS    Active-record diagnostic age
  --asset PATH             Dashboard HTML override
  --worker-script PATH     Snapshot worker override
  -h, --help               Show this help
`;
}

function validateServeArgs(args: string[]) {
  const [workflow, ...options] = args;
  if (!workflow || workflow.startsWith("-")) throw new Error("serve requires WORKFLOW");
  for (let index = 0; index < options.length; index += 2) {
    const option = options[index];
    if (!SERVE_OPTIONS.has(option)) throw new Error(`unknown option: ${option}`);
    if (index + 1 >= options.length || options[index + 1].startsWith("--")) {
      throw new Error(`${option} requires a value`);
    }
  }
  return { workflow, options };
}

if (command === "serve") {
  if (args.includes("--help") || args.includes("-h")) {
    process.stdout.write(serveHelp());
    process.exit(0);
  }
  const { workflow, options } = validateServeArgs(args);
  Bun.argv.splice(2, Bun.argv.length - 2, "--workflow", workflow, ...options);
  await import("./dashboard_server.ts");
} else {
  const worker = fileURLToPath(new URL("workflow_dashboard.py", import.meta.url));
  const child = Bun.spawn(["python3", worker, ...Bun.argv.slice(2)], {
    stdin: "inherit",
    stdout: "inherit",
    stderr: "inherit",
  });
  for (const signal of ["SIGINT", "SIGTERM"] as const) {
    process.on(signal, () => child.kill(signal));
  }
  process.exit(await child.exited);
}
