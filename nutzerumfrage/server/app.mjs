import { createHash, createHmac, randomBytes, scryptSync, timingSafeEqual } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { createServer as createHttpServer } from "node:http";
import { createServer as createHttpsServer } from "node:https";
import { dirname, extname, resolve, sep } from "node:path";
import { DatabaseSync } from "node:sqlite";

const COOKIE_NAME = "survey_admin_session";
const MAX_BODY_BYTES = 1_000_000;
const SCHEMA_VERSION = 1;
const TASK_CODES = ["TASK_OBJECT_PRODUCT", "TASK_HANDOFF_RECEPTION_PRODUCT"];

export const ANSWER_FIELDS = Object.freeze([
  "profile_age_group",
  "profile_activity_field",
  "profile_ai_frequency",
  "q1_device",
  "q1_device_other",
  "q2_experience",
  "q3_object_selection_clarity",
  "q4_object_answer_fit",
  "q5_handoff_observed",
  "q6_handoff_understandability",
  "q7_final_agent_clarity",
  "q8_object_selection_easy",
  "q8_answer_fit",
  "q8_agent_responsibility",
  "q8_predictability",
  "q8_guidance_helpful",
  "q8_overall_ease",
  "q9_error_explanation",
  "q10_agent_selection_model",
  "q11_overall_score",
  "q12_improvement",
  "q13_multi_agent_help",
  "q14_best_use_case",
]);

const REQUIRED_FIELDS = ANSWER_FIELDS.filter(
  (field) => field !== "q1_device_other" && field !== "q12_improvement",
);
const ANSWER_FIELD_SET = new Set(ANSWER_FIELDS);
const LIKERT_FIELDS = new Set([
  "q13_multi_agent_help",
  "q3_object_selection_clarity",
  "q4_object_answer_fit",
  "q8_object_selection_easy",
  "q8_answer_fit",
  "q8_agent_responsibility",
  "q8_predictability",
  "q8_guidance_helpful",
  "q8_overall_ease",
]);
const OPTIONAL_EXPERIENCE_FIELDS = new Set([
  "q6_handoff_understandability",
  "q7_final_agent_clarity",
  "q9_error_explanation",
]);

class ApiError extends Error {
  constructor(status, message, headers = {}) {
    super(message);
    this.status = status;
    this.headers = headers;
  }
}

function isPlainObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function isIsoDate(value) {
  return typeof value === "string" && value.length <= 40 && !Number.isNaN(Date.parse(value));
}

function integerBetween(value, min, max) {
  return Number.isInteger(value) && value >= min && value <= max;
}

function oneOf(value, allowed) {
  return allowed.includes(value);
}

function validateAnswer(field, value) {
  if (field === "profile_age_group") {
    return oneOf(value, ["18_24", "25_34", "35_44", "45_54", "55_64", "65_plus", "no_answer"]);
  }
  if (field === "profile_activity_field") {
    return oneOf(value, [
      "computer_science", "design_hci", "engineering", "business", "education_research",
      "food_production", "other_field", "no_answer",
    ]);
  }
  if (field === "profile_ai_frequency") {
    return oneOf(value, ["never", "less_than_monthly", "monthly", "weekly", "daily"]);
  }
  if (field === "q1_device") {
    return oneOf(value, ["desktop_laptop", "vr_headset", "tablet_smartphone", "other"]);
  }
  if (field === "q1_device_other") {
    return typeof value === "string" && value.trim().length <= 120;
  }
  if (field === "q2_experience") return integerBetween(value, 1, 4);
  if (LIKERT_FIELDS.has(field)) return integerBetween(value, 1, 5);
  if (field === "q5_handoff_observed") return oneOf(value, ["yes", "no", "unsure"]);
  if (OPTIONAL_EXPERIENCE_FIELDS.has(field)) {
    return integerBetween(value, 1, 5) || value === "not_experienced";
  }
  if (field === "q10_agent_selection_model") {
    return oneOf(value, ["object_and_topic", "nearest_agent", "first_contacted", "random", "unclear"]);
  }
  if (field === "q11_overall_score") return integerBetween(value, 0, 10);
  if (field === "q12_improvement") return typeof value === "string" && value.length <= 2000;
  if (field === "q14_best_use_case") {
    const allowed = [
      "trade_fair", "product_information", "museum", "learning", "recruiting",
      "customer_service", "none", "other_use_case",
    ];
    if (typeof value === "string") return oneOf(value, allowed); // Existing records before multiple selection.
    return Array.isArray(value) && value.length > 0 && value.length <= allowed.length &&
      new Set(value).size === value.length && value.every((item) => oneOf(item, allowed)) &&
      (!value.includes("none") || value.length === 1);
  }
  return false;
}

function validateAnswers(value) {
  if (!isPlainObject(value)) throw new ApiError(400, "answers muss ein Objekt sein.");
  for (const [field, answer] of Object.entries(value)) {
    if (!ANSWER_FIELD_SET.has(field)) throw new ApiError(400, `Unbekanntes Antwortfeld: ${field}`);
    if (!validateAnswer(field, answer)) throw new ApiError(400, `Ungültiger Wert für ${field}.`);
  }
  return value;
}

function validateComplete(answers) {
  for (const field of REQUIRED_FIELDS) {
    if (!(field in answers) || !validateAnswer(field, answers[field])) {
      throw new ApiError(400, `Für den Abschluss fehlt eine gültige Antwort: ${field}.`);
    }
  }
  if (answers.q1_device === "other" && !answers.q1_device_other?.trim()) {
    throw new ApiError(400, "Für ein anderes Gerät ist eine Angabe erforderlich.");
  }
}

function validateUuid(value) {
  if (typeof value !== "string" || !/^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(value)) {
    throw new ApiError(400, "Ungültige Teilnahme-ID.");
  }
  return value;
}

function validateToken(value) {
  if (typeof value !== "string" || !/^[A-Za-z0-9_-]{32,128}$/.test(value)) {
    throw new ApiError(400, "Ungültiger Bearbeitungsschlüssel.");
  }
  return value;
}

function tokenHash(token) {
  return createHash("sha256").update(token).digest("hex");
}

function safeEqualText(left, right) {
  const a = Buffer.from(String(left));
  const b = Buffer.from(String(right));
  if (a.length !== b.length) {
    timingSafeEqual(a, Buffer.alloc(a.length));
    return false;
  }
  return timingSafeEqual(a, b);
}

function parseJson(value, fallback) {
  try {
    return JSON.parse(value);
  } catch {
    return fallback;
  }
}

function rowToResponse(row) {
  if (!row) return null;
  return {
    sessionId: row.session_id,
    schemaVersion: row.schema_version,
    status: row.status,
    currentStep: row.current_step,
    revision: row.revision,
    startedAt: row.started_at,
    updatedAt: row.updated_at,
    completedAt: row.completed_at,
    taskCodes: parseJson(row.task_codes_json, TASK_CODES),
    answers: parseJson(row.answers_json, {}),
    answerUpdatedAt: parseJson(row.answer_updated_at_json, {}),
  };
}

function openDatabase(dbPath) {
  if (dbPath !== ":memory:") mkdirSync(dirname(resolve(dbPath)), { recursive: true });
  const db = new DatabaseSync(dbPath);
  db.exec("PRAGMA foreign_keys = ON");
  db.exec("PRAGMA busy_timeout = 5000");
  db.exec("PRAGMA synchronous = FULL");
  if (dbPath !== ":memory:") db.exec("PRAGMA journal_mode = WAL");
  db.exec(`
    CREATE TABLE IF NOT EXISTS responses (
      session_id TEXT PRIMARY KEY,
      edit_token_hash TEXT NOT NULL,
      schema_version INTEGER NOT NULL,
      status TEXT NOT NULL CHECK (status IN ('draft', 'completed')),
      current_step INTEGER NOT NULL,
      revision INTEGER NOT NULL,
      started_at TEXT NOT NULL,
      updated_at TEXT NOT NULL,
      completed_at TEXT,
      task_codes_json TEXT NOT NULL,
      answers_json TEXT NOT NULL,
      answer_updated_at_json TEXT NOT NULL
    ) STRICT;
    CREATE INDEX IF NOT EXISTS responses_updated_idx ON responses(updated_at DESC);
    CREATE INDEX IF NOT EXISTS responses_status_idx ON responses(status, updated_at DESC);
  `);
  return db;
}

function openRaffleDatabase(dbPath) {
  if (dbPath !== ":memory:") mkdirSync(dirname(resolve(dbPath)), { recursive: true });
  const db = new DatabaseSync(dbPath);
  db.exec("PRAGMA busy_timeout = 5000");
  db.exec("PRAGMA synchronous = FULL");
  if (dbPath !== ":memory:") db.exec("PRAGMA journal_mode = WAL");
  db.exec(`
    CREATE TABLE IF NOT EXISTS raffle_entries (
      study_identifier TEXT PRIMARY KEY,
      eligibility_hash TEXT NOT NULL UNIQUE
    ) STRICT;
  `);
  return db;
}

function readBody(request) {
  return new Promise((resolveBody, reject) => {
    const chunks = [];
    let size = 0;
    request.on("data", (chunk) => {
      size += chunk.length;
      if (size > MAX_BODY_BYTES) {
        reject(new ApiError(413, "Anfrage ist zu groß."));
        request.destroy();
        return;
      }
      chunks.push(chunk);
    });
    request.on("end", () => {
      if (chunks.length === 0) return resolveBody({});
      try {
        const parsed = JSON.parse(Buffer.concat(chunks).toString("utf8"));
        if (!isPlainObject(parsed)) throw new Error("not an object");
        resolveBody(parsed);
      } catch {
        reject(new ApiError(400, "Ungültige JSON-Anfrage."));
      }
    });
    request.on("error", reject);
  });
}

function securityHeaders(extra = {}) {
  return {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "X-Frame-Options": "SAMEORIGIN",
    ...extra,
  };
}

function sendJson(response, status, payload, headers = {}) {
  const body = Buffer.from(JSON.stringify(payload));
  response.writeHead(status, securityHeaders({
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": body.length,
    "Cache-Control": "no-store",
    ...headers,
  }));
  response.end(body);
}

function getBearer(request) {
  const match = request.headers.authorization?.match(/^Bearer\s+(.+)$/i);
  if (!match) throw new ApiError(401, "Bearbeitungsschlüssel fehlt.");
  return validateToken(match[1]);
}

function cookies(request) {
  const result = {};
  for (const part of (request.headers.cookie ?? "").split(";")) {
    const index = part.indexOf("=");
    if (index < 1) continue;
    result[part.slice(0, index).trim()] = decodeURIComponent(part.slice(index + 1).trim());
  }
  return result;
}

function mergeAnswers(currentAnswers, currentTimes, incomingAnswers, incomingTimes, fallbackTime) {
  const answers = { ...currentAnswers };
  const timestamps = { ...currentTimes };
  for (const [field, value] of Object.entries(incomingAnswers)) {
    const incomingAt = isIsoDate(incomingTimes[field]) ? incomingTimes[field] : fallbackTime;
    const currentAt = isIsoDate(timestamps[field]) ? timestamps[field] : "";
    if (!currentAt || Date.parse(incomingAt) >= Date.parse(currentAt)) {
      answers[field] = value;
      timestamps[field] = incomingAt;
    }
  }
  if (answers.q1_device !== "other") {
    delete answers.q1_device_other;
    delete timestamps.q1_device_other;
  }
  return { answers, timestamps };
}

function normalizeTaskCodes(value) {
  if (value === undefined) return TASK_CODES;
  if (!Array.isArray(value) || value.length > 10 || value.some((item) => typeof item !== "string" || item.length > 100)) {
    throw new ApiError(400, "Ungültige Task-Codes.");
  }
  return value;
}

function validateWritePayload(body, now) {
  if (!integerBetween(body.revision, 0, Number.MAX_SAFE_INTEGER)) throw new ApiError(400, "Ungültige Revision.");
  if (!integerBetween(body.currentStep, 1, 4)) throw new ApiError(400, "Ungültiger Fragebogenschritt.");
  if (!oneOf(body.status, ["draft", "completed"])) throw new ApiError(400, "Ungültiger Status.");
  const answers = validateAnswers(body.answers ?? {});
  const answerUpdatedAt = body.answerUpdatedAt ?? {};
  if (!isPlainObject(answerUpdatedAt)) throw new ApiError(400, "answerUpdatedAt muss ein Objekt sein.");
  for (const [field, timestamp] of Object.entries(answerUpdatedAt)) {
    if (!ANSWER_FIELD_SET.has(field) || !isIsoDate(timestamp)) throw new ApiError(400, `Ungültiger Antwortzeitpunkt: ${field}.`);
  }
  if (!isIsoDate(body.startedAt)) throw new ApiError(400, "Ungültiger Startzeitpunkt.");
  if (body.schemaVersion !== undefined && body.schemaVersion !== SCHEMA_VERSION) throw new ApiError(400, "Nicht unterstützte Fragebogenversion.");
  return {
    revision: body.revision,
    currentStep: body.currentStep,
    status: body.status,
    answers,
    answerUpdatedAt,
    startedAt: body.startedAt,
    schemaVersion: body.schemaVersion ?? SCHEMA_VERSION,
    taskCodes: normalizeTaskCodes(body.taskCodes),
    now,
  };
}

function csvCell(value) {
  let text = value === null || value === undefined ? "" : typeof value === "string" ? value : JSON.stringify(value);
  if (/^[=+\-@\t\r]/.test(text)) text = `'${text}`;
  return `"${text.replaceAll('"', '""')}"`;
}

function responsesToCsv(responses) {
  const headers = [
    "session_id", "status", "schema_version", "current_step", "revision",
    "started_at", "updated_at", "completed_at", "task_codes", ...ANSWER_FIELDS,
  ];
  const rows = responses.map((record) => [
    record.sessionId,
    record.status,
    record.schemaVersion,
    record.currentStep,
    record.revision,
    record.startedAt,
    record.updatedAt,
    record.completedAt ?? "",
    record.taskCodes,
    ...ANSWER_FIELDS.map((field) => record.answers[field] ?? ""),
  ]);
  return `\uFEFF${[headers, ...rows].map((row) => row.map(csvCell).join(",")).join("\r\n")}\r\n`;
}

const MIME_TYPES = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".wasm": "application/wasm",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".ico": "image/x-icon",
  ".svg": "image/svg+xml",
  ".br": "application/octet-stream",
};

function serveStatic(request, response, staticDir, pathname) {
  if (!staticDir || !["GET", "HEAD"].includes(request.method)) return false;
  const root = resolve(staticDir);
  let decoded;
  try {
    decoded = decodeURIComponent(pathname);
  } catch {
    throw new ApiError(400, "Ungültiger Pfad.");
  }
  const relative = decoded === "/" ? "index.html" : decoded.replace(/^\/+/, "");
  const file = resolve(root, relative);
  if (file !== root && !file.startsWith(`${root}${sep}`)) throw new ApiError(403, "Zugriff verweigert.");
  if (!existsSync(file) || !statSync(file).isFile()) return false;

  let contentType = MIME_TYPES[extname(file).toLowerCase()] ?? "application/octet-stream";
  const headers = securityHeaders({ "Content-Type": contentType, "Cache-Control": file.endsWith(".html") ? "no-cache" : "public, max-age=3600" });
  if (file.endsWith(".br")) {
    headers["Content-Encoding"] = "br";
    if (file.endsWith(".wasm.br")) contentType = "application/wasm";
    else if (file.endsWith(".js.br")) contentType = "text/javascript; charset=utf-8";
    headers["Content-Type"] = contentType;
  }
  const body = readFileSync(file);
  response.writeHead(200, { ...headers, "Content-Length": body.length });
  response.end(request.method === "HEAD" ? undefined : body);
  return true;
}

export function createSurveyServer(options = {}) {
  const now = options.now ?? (() => new Date());
  const db = openDatabase(options.dbPath ?? ":memory:");
  const raffleDb = openRaffleDatabase(options.raffleDbPath ?? ":memory:");
  const raffleSecret = String(options.raffleSecret ?? randomBytes(32).toString("base64url"));
  const adminPin = String(options.adminPin ?? "");
  if (adminPin.length < 4) throw new Error("SURVEY_ADMIN_PIN muss mindestens vier Zeichen lang sein.");
  const secureCookie = options.secureCookie ?? true;
  const staticDir = options.staticDir ? resolve(options.staticDir) : null;
  const sessionTtlMs = options.sessionTtlMs ?? 30 * 60 * 1000;
  const pinSalt = randomBytes(16);
  const expectedPinHash = scryptSync(adminPin, pinSalt, 32);
  const adminSessions = new Map();
  const failedLogins = new Map();
  const loginWindowMs = options.loginWindowMs ?? 10 * 60 * 1000;
  const maxLoginAttempts = options.maxLoginAttempts ?? 8;
  const insertRaffle = raffleDb.prepare("INSERT INTO raffle_entries (study_identifier, eligibility_hash) VALUES (?, ?)");
  const selectRaffle = raffleDb.prepare("SELECT study_identifier FROM raffle_entries ORDER BY study_identifier COLLATE NOCASE");

  function issueEligibilityToken(editToken) {
    const nonce = createHmac("sha256", raffleSecret).update(`eligibility:${editToken}`).digest("base64url");
    const signature = createHmac("sha256", raffleSecret).update(nonce).digest("base64url");
    return `${nonce}.${signature}`;
  }

  function validateEligibilityToken(value) {
    const token = String(value ?? "");
    const [nonce, signature, extra] = token.split(".");
    if (!nonce || !signature || extra) throw new ApiError(403, "Berechtigung für die Verlosung ist ungültig.");
    const expected = createHmac("sha256", raffleSecret).update(nonce).digest("base64url");
    if (!safeEqualText(signature, expected)) throw new ApiError(403, "Berechtigung für die Verlosung ist ungültig.");
    return tokenHash(token);
  }

  function clientAddress(request) {
    const forwarded = request.headers["x-forwarded-for"];
    if (typeof forwarded === "string" && forwarded.trim()) {
      return forwarded.split(",", 1)[0].trim();
    }
    return request.socket.remoteAddress ?? "unknown";
  }

  const selectById = db.prepare("SELECT * FROM responses WHERE session_id = ?");
  const selectAll = db.prepare("SELECT * FROM responses ORDER BY updated_at DESC, session_id DESC");
  const deleteAll = db.prepare("DELETE FROM responses");
  const insert = db.prepare(`
    INSERT INTO responses (
      session_id, edit_token_hash, schema_version, status, current_step, revision,
      started_at, updated_at, completed_at, task_codes_json, answers_json, answer_updated_at_json
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);
  const update = db.prepare(`
    UPDATE responses SET
      schema_version = ?, status = ?, current_step = ?, revision = ?, updated_at = ?,
      completed_at = ?, task_codes_json = ?, answers_json = ?, answer_updated_at_json = ?
    WHERE session_id = ?
  `);

  function getRecord(id) {
    return rowToResponse(selectById.get(id));
  }

  function requireEditToken(request, row) {
    const token = getBearer(request);
    if (!safeEqualText(tokenHash(token), row.edit_token_hash)) throw new ApiError(403, "Bearbeitungsschlüssel ist ungültig.");
    return token;
  }

  function adminSession(request) {
    const token = cookies(request)[COOKIE_NAME];
    if (!token) return null;
    const hash = tokenHash(token);
    const session = adminSessions.get(hash);
    const timestamp = now().getTime();
    if (!session || session.expiresAt <= timestamp) {
      adminSessions.delete(hash);
      return null;
    }
    session.expiresAt = timestamp + sessionTtlMs;
    return { token, hash, session };
  }

  function requireAdmin(request) {
    const session = adminSession(request);
    if (!session) throw new ApiError(401, "Anmeldung erforderlich.");
    return session;
  }

  function cookieHeader(token, maxAge) {
    return `${COOKIE_NAME}=${encodeURIComponent(token)}; Path=/; HttpOnly; SameSite=Strict; Max-Age=${maxAge}${secureCookie ? "; Secure" : ""}`;
  }

  async function handleApi(request, response, url) {
    const pathname = url.pathname;

    if (pathname === "/api/health" && request.method === "GET") {
      return sendJson(response, 200, { ok: true });
    }

    if (pathname === "/api/responses" && request.method === "POST") {
      const body = await readBody(request);
      const sessionId = validateUuid(body.sessionId);
      const editToken = validateToken(body.editToken);
      if (body.schemaVersion !== SCHEMA_VERSION) throw new ApiError(400, "Nicht unterstützte Fragebogenversion.");
      if (!isIsoDate(body.startedAt)) throw new ApiError(400, "Ungültiger Startzeitpunkt.");
      const existingRow = selectById.get(sessionId);
      if (existingRow) {
        if (!safeEqualText(tokenHash(editToken), existingRow.edit_token_hash)) throw new ApiError(409, "Teilnahme-ID wird bereits verwendet.");
        return sendJson(response, 200, { response: rowToResponse(existingRow) });
      }
      const timestamp = now().toISOString();
      insert.run(
        sessionId, tokenHash(editToken), SCHEMA_VERSION, "draft", 1, 0,
        body.startedAt, timestamp, null, JSON.stringify(normalizeTaskCodes(body.taskCodes)), "{}", "{}",
      );
      return sendJson(response, 201, { response: getRecord(sessionId) });
    }

    const responseMatch = pathname.match(/^\/api\/responses\/([0-9a-f-]+)$/i);
    if (responseMatch && request.method === "GET") {
      const sessionId = validateUuid(responseMatch[1]);
      const row = selectById.get(sessionId);
      if (!row) throw new ApiError(404, "Teilnahme nicht gefunden.");
      requireEditToken(request, row);
      return sendJson(response, 200, { response: rowToResponse(row) });
    }

    if (responseMatch && request.method === "PUT") {
      const sessionId = validateUuid(responseMatch[1]);
      const token = getBearer(request);
      const body = await readBody(request);
      const timestamp = now().toISOString();
      const incoming = validateWritePayload(body, timestamp);
      let row = selectById.get(sessionId);

      if (!row) {
        const completedAt = incoming.status === "completed" ? timestamp : null;
        if (incoming.status === "completed") validateComplete(incoming.answers);
        insert.run(
          sessionId, tokenHash(token), incoming.schemaVersion, incoming.status,
          incoming.currentStep, incoming.revision, incoming.startedAt, timestamp, completedAt,
          JSON.stringify(incoming.taskCodes), JSON.stringify(incoming.answers), JSON.stringify(incoming.answerUpdatedAt),
        );
        return sendJson(response, 200, { response: getRecord(sessionId) });
      }

      if (!safeEqualText(tokenHash(token), row.edit_token_hash)) throw new ApiError(403, "Bearbeitungsschlüssel ist ungültig.");
      const current = rowToResponse(row);
      if (current.status === "completed") return sendJson(response, 200, { response: current });

      const merged = mergeAnswers(
        current.answers,
        current.answerUpdatedAt,
        incoming.answers,
        incoming.answerUpdatedAt,
        timestamp,
      );
      const completes = incoming.status === "completed";
      if (completes) validateComplete(merged.answers);
      const incomingIsCurrent = incoming.revision >= current.revision;
      const nextStatus = completes ? "completed" : "draft";
      const nextRevision = Math.max(current.revision, incoming.revision);
      const nextStep = completes ? 4 : incomingIsCurrent ? incoming.currentStep : current.currentStep;
      const taskCodes = incomingIsCurrent ? incoming.taskCodes : current.taskCodes;
      update.run(
        current.schemaVersion,
        nextStatus,
        nextStep,
        nextRevision,
        timestamp,
        completes ? timestamp : null,
        JSON.stringify(taskCodes),
        JSON.stringify(merged.answers),
        JSON.stringify(merged.timestamps),
        sessionId,
      );
      return sendJson(response, 200, { response: getRecord(sessionId) });
    }

    if (pathname === "/api/raffle-eligibility" && request.method === "POST") {
      const body = await readBody(request);
      const row = selectById.get(validateUuid(body.sessionId));
      if (!row) throw new ApiError(404, "Teilnahme nicht gefunden.");
      const editToken = requireEditToken(request, row);
      if (row.status !== "completed") throw new ApiError(409, "Die Verlosung wird erst nach dem vollständig ausgefüllten Fragebogen freigeschaltet.");
      return sendJson(response, 200, { eligibilityToken: issueEligibilityToken(editToken) });
    }

    if (pathname === "/api/raffle-entry" && request.method === "POST") {
      const body = await readBody(request);
      const identifier = String(body.studyIdentifier ?? "").trim().replace(/\s+/g, " ");
      if (identifier.length < 3 || identifier.length > 120) throw new ApiError(400, "Die Studierendenkennung muss 3 bis 120 Zeichen lang sein.");
      const eligibilityHash = validateEligibilityToken(body.eligibilityToken);
      try {
        insertRaffle.run(identifier, eligibilityHash);
      } catch (error) {
        if (String(error?.message).includes("UNIQUE")) throw new ApiError(409, "Diese Studierendenkennung oder Teilnahme wurde bereits für die Verlosung eingetragen.");
        throw error;
      }
      return sendJson(response, 201, { registered: true });
    }

    if (["/api/admin/login", "/api/admin/session"].includes(pathname) && request.method === "POST") {
      const address = clientAddress(request);
      const timestamp = now().getTime();
      const recent = (failedLogins.get(address) ?? []).filter((attempt) => timestamp - attempt < loginWindowMs);
      if (recent.length >= maxLoginAttempts) {
        throw new ApiError(429, "Zu viele Anmeldeversuche. Bitte warten Sie.", { "Retry-After": String(Math.ceil(loginWindowMs / 1000)) });
      }
      const body = await readBody(request);
      const submitted = scryptSync(String(body.pin ?? ""), pinSalt, 32);
      const valid = timingSafeEqual(submitted, expectedPinHash);
      if (!valid) {
        recent.push(timestamp);
        failedLogins.set(address, recent);
        throw new ApiError(401, "Die PIN ist nicht korrekt.");
      }
      failedLogins.delete(address);
      const token = randomBytes(32).toString("base64url");
      adminSessions.set(tokenHash(token), { expiresAt: timestamp + sessionTtlMs });
      return sendJson(response, 200, { ok: true }, { "Set-Cookie": cookieHeader(token, Math.floor(sessionTtlMs / 1000)) });
    }

    if (
      (pathname === "/api/admin/logout" && request.method === "POST") ||
      (pathname === "/api/admin/session" && request.method === "DELETE")
    ) {
      const session = adminSession(request);
      if (session) adminSessions.delete(session.hash);
      return sendJson(response, 200, { ok: true }, { "Set-Cookie": cookieHeader("", 0) });
    }

    if (pathname === "/api/admin/responses" && request.method === "GET") {
      requireAdmin(request);
      const responses = selectAll.all().map(rowToResponse);
      return sendJson(response, 200, { responses });
    }

    if (pathname === "/api/admin/responses" && request.method === "DELETE") {
      requireAdmin(request);
      const result = deleteAll.run();
      return sendJson(response, 200, { deleted: Number(result.changes) });
    }

    if (pathname === "/api/admin/export.json" && request.method === "GET") {
      requireAdmin(request);
      const records = selectAll.all().map(rowToResponse);
      const payload = Buffer.from(JSON.stringify({ exportedAt: now().toISOString(), responses: records }, null, 2));
      const filename = `fragebogen-antworten-${now().toISOString().slice(0, 10)}.json`;
      response.writeHead(200, securityHeaders({
        "Content-Type": "application/json; charset=utf-8",
        "Content-Length": payload.length,
        "Content-Disposition": `attachment; filename="${filename}"`,
        "Cache-Control": "no-store",
      }));
      return response.end(payload);
    }

    if (pathname === "/api/admin/export.csv" && request.method === "GET") {
      requireAdmin(request);
      const records = selectAll.all().map(rowToResponse);
      const payload = Buffer.from(responsesToCsv(records), "utf8");
      const filename = `fragebogen-antworten-${now().toISOString().slice(0, 10)}.csv`;
      response.writeHead(200, securityHeaders({
        "Content-Type": "text/csv; charset=utf-8",
        "Content-Length": payload.length,
        "Content-Disposition": `attachment; filename="${filename}"`,
        "Cache-Control": "no-store",
      }));
      return response.end(payload);
    }

    if (pathname === "/api/admin/raffle/export.csv" && request.method === "GET") {
      requireAdmin(request);
      const rows = selectRaffle.all();
      const escape = (value) => `"${String(value).replaceAll('"', '""')}"`;
      const payload = Buffer.from(`studierendenkennung\r\n${rows.map((row) => escape(row.study_identifier)).join("\r\n")}${rows.length ? "\r\n" : ""}`, "utf8");
      response.writeHead(200, securityHeaders({
        "Content-Type": "text/csv; charset=utf-8",
        "Content-Length": payload.length,
        "Content-Disposition": `attachment; filename="verlosung-kennungen-${now().toISOString().slice(0, 10)}.csv"`,
        "Cache-Control": "no-store",
      }));
      return response.end(payload);
    }

    if (pathname === "/api/admin/raffle" && request.method === "GET") {
      requireAdmin(request);
      return sendJson(response, 200, { identifiers: selectRaffle.all().map((row) => row.study_identifier) });
    }

    throw new ApiError(404, "API-Endpunkt nicht gefunden.");
  }

  const handler = async (request, response) => {
    try {
      const url = new URL(request.url ?? "/", `http://${request.headers.host ?? "localhost"}`);
      if (url.pathname.startsWith("/api/")) return await handleApi(request, response, url);
      if (serveStatic(request, response, staticDir, url.pathname)) return;
      throw new ApiError(404, "Seite nicht gefunden.");
    } catch (error) {
      if (response.headersSent) return response.end();
      const status = error instanceof ApiError ? error.status : 500;
      if (!(error instanceof ApiError)) console.error(error);
      sendJson(response, status, { error: status === 500 ? "Interner Serverfehler." : error.message }, error.headers);
    }
  };

  const server = options.tls
    ? createHttpsServer(options.tls, handler)
    : createHttpServer(handler);

  return {
    server,
    database: db,
    async listen(port = 0, host = "127.0.0.1") {
      await new Promise((resolveListen, reject) => {
        server.once("error", reject);
        server.listen(port, host, () => {
          server.off("error", reject);
          resolveListen();
        });
      });
      return server.address();
    },
    async close() {
      if (server.listening) await new Promise((resolveClose, reject) => server.close((error) => error ? reject(error) : resolveClose()));
      db.close();
      raffleDb.close();
    },
  };
}
