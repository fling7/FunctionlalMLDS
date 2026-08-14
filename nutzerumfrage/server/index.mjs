import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { createSurveyServer } from "./app.mjs";

function loadEnv(path) {
  if (!existsSync(path)) return;
  for (const rawLine of readFileSync(path, "utf8").split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;
    const index = line.indexOf("=");
    if (index < 1) continue;
    const key = line.slice(0, index).trim();
    let value = line.slice(index + 1).trim();
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    if (!(key in process.env)) process.env[key] = value;
  }
}

loadEnv(resolve(".env"));

const serve = process.argv.includes("--serve");
function readSecret(valueName, fileName) {
  const direct = process.env[valueName]?.trim();
  const file = process.env[fileName]?.trim();
  if (direct && file) throw new Error(`${valueName} und ${fileName} dürfen nicht gleichzeitig gesetzt sein.`);
  if (direct) return direct;
  if (!file) return "";
  return readFileSync(resolve(file), "utf8").trim();
}

const adminPin = readSecret("SURVEY_ADMIN_PIN", "SURVEY_ADMIN_PIN_FILE");
const forbiddenPins = new Set(["1234", "0000", "admin", "replace-with-a-long-private-pin"]);
if (adminPin.length < 6 || forbiddenPins.has(adminPin.toLowerCase())) {
  console.error("SURVEY_ADMIN_PIN fehlt oder ist zu schwach. Bitte .env.example nach .env kopieren und eine private PIN setzen.");
  process.exit(1);
}

const options = {
  dbPath: resolve(process.env.SURVEY_DB_PATH ?? "./data/survey.sqlite"),
  raffleDbPath: resolve(process.env.SURVEY_RAFFLE_DB_PATH ?? "./data/raffle.sqlite"),
  raffleSecret: readSecret("SURVEY_RAFFLE_SECRET", "SURVEY_RAFFLE_SECRET_FILE"),
  adminPin,
  staticDir: serve ? resolve("dist") : null,
  secureCookie: process.env.SURVEY_SECURE_COOKIE !== "false",
};

if (options.raffleSecret.length < 32) {
  console.error("SURVEY_RAFFLE_SECRET fehlt oder ist zu kurz (mindestens 32 Zeichen).");
  process.exit(1);
}

if (serve) {
  const keyPath = resolve(process.env.SURVEY_TLS_KEY ?? "./keys/localhost-key.pem");
  const certPath = resolve(process.env.SURVEY_TLS_CERT ?? "./keys/localhost-cert.pem");
  options.tls = { key: readFileSync(keyPath), cert: readFileSync(certPath) };
}

const app = createSurveyServer(options);
const port = Number(serve ? process.env.SURVEY_HTTPS_PORT ?? 3443 : process.env.SURVEY_API_PORT ?? 3001);
const host = serve ? "0.0.0.0" : process.env.SURVEY_API_HOST ?? "127.0.0.1";
await app.listen(port, host);
console.log(serve ? `Studienseite: https://localhost:${port}` : `Antwortspeicher: http://${host}:${port}`);

let stopping = false;
async function stop() {
  if (stopping) return;
  stopping = true;
  await app.close();
  process.exit(0);
}
process.on("SIGINT", stop);
process.on("SIGTERM", stop);
