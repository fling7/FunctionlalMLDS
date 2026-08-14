import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";

const viteCli = fileURLToPath(new URL("../node_modules/vite/bin/vite.js", import.meta.url));

const children = [
  spawn(process.execPath, ["server/index.mjs"], {
    stdio: "inherit",
    env: process.env,
  }),
  // Start Vite through the current Node executable. Spawning npm.cmd directly
  // can fail with EINVAL on Windows/Node 22, especially from paths with spaces.
  spawn(process.execPath, [viteCli], {
    stdio: "inherit",
    env: process.env,
  }),
];

let stopping = false;
function stop(code = 0) {
  if (stopping) return;
  stopping = true;
  for (const child of children) {
    if (!child.killed) child.kill();
  }
  setTimeout(() => process.exit(code), 60).unref();
}

for (const child of children) {
  child.on("exit", (code, signal) => {
    if (!stopping && code !== 0) {
      console.error(`Entwicklungsprozess wurde beendet (${signal ?? code}).`);
      stop(code ?? 1);
    }
  });
}

process.on("SIGINT", () => stop(0));
process.on("SIGTERM", () => stop(0));
