#!/usr/bin/env bun

import { fileURLToPath } from "node:url";

type JsonObject = Record<string, unknown>;

const DEFAULT_REFRESH_MS = 30_000;
const WORKER_TIMEOUT_MS = 120_000;

function argumentsFrom(argv: string[]) {
  const allowed = new Set([
    "--workflow",
    "--host",
    "--port",
    "--capacity",
    "--refresh-ms",
    "--stale-after",
    "--sessions-root",
    "--claude-sessions-root",
    "--asset",
    "--worker-script",
  ]);
  const values = new Map<string, string[]>();
  for (let index = 0; index < argv.length; index += 1) {
    const key = argv[index];
    if (!key.startsWith("--") || index + 1 >= argv.length) throw new Error(`invalid argument: ${key}`);
    if (!allowed.has(key)) throw new Error(`unknown option: ${key}`);
    const value = argv[index + 1];
    values.set(key, [...(values.get(key) || []), value]);
    index += 1;
  }
  const one = (key: string, fallback?: string) => values.get(key)?.at(-1) ?? fallback;
  const workflow = one("--workflow");
  if (!workflow) throw new Error("--workflow is required");
  const host = one("--host", "127.0.0.1")!;
  if (host !== "127.0.0.1") throw new Error("dashboard host must be 127.0.0.1");
  const port = Number(one("--port", "0"));
  const capacityText = one("--capacity");
  const capacity = capacityText === undefined ? null : Number(capacityText);
  const refreshMs = Number(one("--refresh-ms", String(DEFAULT_REFRESH_MS)));
  const staleAfter = Number(one("--stale-after", "600"));
  if (!Number.isInteger(port) || port < 0 || port > 65_535) throw new Error("invalid dashboard port");
  if (capacity !== null && (!Number.isInteger(capacity) || capacity < 1)) throw new Error("invalid capacity");
  if (!Number.isInteger(refreshMs) || refreshMs < 10) throw new Error("invalid refresh interval");
  if (!Number.isInteger(staleAfter) || staleAfter < 1) throw new Error("invalid stale interval");
  return {
    workflow,
    host,
    port,
    capacity,
    refreshMs,
    staleAfter,
    roots: values.get("--sessions-root") || [],
    claudeRoots: values.get("--claude-sessions-root") || [],
    asset: one("--asset", fileURLToPath(new URL("dashboard.html", import.meta.url)))!,
    workerScript: one("--worker-script", fileURLToPath(new URL("workflow_dashboard.py", import.meta.url)))!,
  };
}

class SnapshotWorker {
  private process: any = null;
  private pending: null | { id: number; resolve: (value: any) => void; reject: (error: Error) => void; timer: Timer } = null;
  private buffer = "";
  private requestId = 0;

  constructor(private readonly command: string[], private readonly onUpdate: (message: any) => void) {}

  private start() {
    if (this.process) return;
    this.buffer = "";
    const child = Bun.spawn(this.command, { stdin: "pipe", stdout: "pipe", stderr: "pipe" });
    this.process = child;
    void this.read(child);
    void new Response(child.stderr).text();
    void child.exited.then(() => {
      if (this.process !== child) return;
      this.process = null;
      this.fail(new Error("snapshot worker exited"));
    });
  }

  private async read(child: any) {
    const decoder = new TextDecoder();
    for await (const chunk of child.stdout) {
      this.buffer += decoder.decode(chunk, { stream: true });
      let newline = this.buffer.indexOf("\n");
      while (newline >= 0) {
        const line = this.buffer.slice(0, newline);
        this.buffer = this.buffer.slice(newline + 1);
        this.receive(line);
        newline = this.buffer.indexOf("\n");
      }
    }
  }

  private receive(line: string) {
    try {
      const response = JSON.parse(line);
      if (response.kind === "update") {
        this.onUpdate(response);
        return;
      }
      if (!this.pending || response.kind !== "response" || response.id !== this.pending.id) return;
      const pending = this.pending;
      this.pending = null;
      clearTimeout(pending.timer);
      if (!response.ok || !response.snapshot) {
        pending.reject(new Error(response.error || "snapshot unavailable"));
        return;
      }
      pending.resolve(response);
    } catch (error) {
      this.fail(error instanceof Error ? error : new Error("invalid worker response"));
    }
  }

  private fail(error: Error) {
    if (!this.pending) return;
    const pending = this.pending;
    this.pending = null;
    clearTimeout(pending.timer);
    pending.reject(error);
  }

  request(): Promise<any> {
    if (this.pending) return Promise.reject(new Error("snapshot refresh already running"));
    this.start();
    return new Promise((resolve, reject) => {
      const id = ++this.requestId;
      const timer = setTimeout(() => {
        this.fail(new Error("snapshot refresh timed out"));
        this.process?.kill();
        this.process = null;
      }, WORKER_TIMEOUT_MS);
      this.pending = { id, resolve, reject, timer };
      this.process.stdin.write(JSON.stringify({ id, command: "snapshot" }) + "\n");
      this.process.stdin.flush();
    });
  }

  close() {
    this.fail(new Error("snapshot worker stopped"));
    this.process?.kill();
    this.process = null;
  }
}

const options = argumentsFrom(Bun.argv.slice(2));
const workerCommand = ["python3", options.workerScript, "snapshot-worker", options.workflow];
for (const root of options.roots) workerCommand.push("--sessions-root", root);
for (const root of options.claudeRoots) workerCommand.push("--claude-sessions-root", root);
if (options.capacity !== null) workerCommand.push("--capacity", String(options.capacity));
workerCommand.push("--stale-after", String(options.staleAfter));

let sequence = 0;
let requestInFlight = false;
let telemetryRefreshing = false;
let refreshError: string | null = null;
let refreshTimer: Timer | null = null;
let snapshot: JsonObject = {
  generated_at: new Date().toISOString(),
  run: { workflow: options.workflow, mode: "loading" },
  summary: { capacity: options.capacity, ready: 0, active: 0, tickets_blocked: 0, active_agents: 0, pipeline_progress: 0 },
  tickets: [],
  agents: [],
  alerts: [],
  telemetry_available: false,
};
function acceptSnapshot(candidate: JsonObject) {
  const changed = sequence === 0 || candidate.generated_at !== snapshot.generated_at;
  snapshot = candidate;
  if (changed) sequence += 1;
}
const worker = new SnapshotWorker(workerCommand, (message) => {
  telemetryRefreshing = Boolean(message.refreshing);
  if (message.ok && message.snapshot) {
    acceptSnapshot(message.snapshot);
    refreshError = null;
  } else {
    refreshError = "snapshot_unavailable";
  }
});

try {
  const initial = await worker.request();
  acceptSnapshot(initial.snapshot);
  telemetryRefreshing = Boolean(initial.refreshing);
} catch {
  refreshError = "snapshot_unavailable";
}

async function refresh() {
  if (requestInFlight) return;
  requestInFlight = true;
  try {
    const response = await worker.request();
    acceptSnapshot(response.snapshot);
    telemetryRefreshing = Boolean(response.refreshing);
  } catch {
    refreshError = "snapshot_unavailable";
  } finally {
    requestInFlight = false;
    refreshTimer = setTimeout(refresh, options.refreshMs);
  }
}

function headers(contentType: string) {
  return {
    "Cache-Control": "no-store",
    "Content-Security-Policy": "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:",
    "Content-Type": contentType,
    "X-Content-Type-Options": "nosniff",
  };
}

const server = Bun.serve({
  hostname: options.host,
  port: options.port,
  async fetch(request) {
    const url = new URL(request.url);
    if (request.method !== "GET") return new Response("Method Not Allowed\n", { status: 405, headers: headers("text/plain; charset=utf-8") });
    if (url.pathname === "/") {
      const asset = Bun.file(options.asset);
      if (!(await asset.exists())) return new Response("Dashboard asset unavailable\n", { status: 500, headers: headers("text/plain; charset=utf-8") });
      return new Response(asset, { headers: headers("text/html; charset=utf-8") });
    }
    if (url.pathname === "/health") return new Response("ok\n", { headers: headers("text/plain; charset=utf-8") });
    if (url.pathname === "/api/status") {
      return Response.json({
        ...snapshot,
        snapshot_sequence: sequence,
        telemetry_refreshing: telemetryRefreshing,
        telemetry_refresh_error: refreshError,
      }, { headers: headers("application/json") });
    }
    return new Response("Not Found\n", { status: 404, headers: headers("text/plain; charset=utf-8") });
  },
});

console.log(JSON.stringify({ url: `http://${options.host}:${server.port}`, pid: process.pid, host: options.host, port: server.port }));
refreshTimer = setTimeout(refresh, options.refreshMs);

function stop() {
  if (refreshTimer) clearTimeout(refreshTimer);
  worker.close();
  server.stop(true);
  process.exit(0);
}

process.on("SIGINT", stop);
process.on("SIGTERM", stop);
