import assert from "node:assert/strict";
import { brotliCompressSync } from "node:zlib";
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { get as httpGet } from "node:http";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { createSurveyServer } from "../server/app.mjs";

const TASK_CODES = ["TASK_OBJECT_PRODUCT", "TASK_HANDOFF_RECEPTION_PRODUCT"];

function makeSession() {
  return {
    sessionId: crypto.randomUUID(),
    editToken: "abcdefghijklmnopqrstuvwxyzABCDEFGH12345678_-",
    startedAt: "2026-08-13T10:00:00.000Z",
    schemaVersion: 1,
    taskCodes: TASK_CODES,
  };
}

function fullAnswers(improvement = "Mehr sichtbare Hinweise") {
  return {
    profile_age_group: "25_34",
    profile_activity_field: "computer_science",
    profile_ai_frequency: "weekly",
    q1_device: "desktop_laptop",
    q2_experience: 3,
    q3_object_selection_clarity: 4,
    q4_object_answer_fit: 5,
    q5_handoff_observed: "yes",
    q6_handoff_understandability: 4,
    q7_final_agent_clarity: 5,
    q8_object_selection_easy: 4,
    q8_answer_fit: 5,
    q8_agent_responsibility: 4,
    q8_predictability: 3,
    q8_guidance_helpful: 4,
    q8_overall_ease: 4,
    q9_error_explanation: "not_experienced",
    q10_agent_selection_model: "object_and_topic",
    q11_overall_score: 8,
    q12_improvement: improvement,
    q13_multi_agent_help: 4,
    q14_best_use_case: ["learning", "museum"],
  };
}

function timestamps(answers, value = "2026-08-13T10:01:00.000Z") {
  return Object.fromEntries(Object.keys(answers).map((key) => [key, value]));
}

async function start(options = {}) {
  const app = createSurveyServer({
    dbPath: ":memory:",
    adminPin: "24681012",
    secureCookie: false,
    ...options,
  });
  const address = await app.listen(0);
  return { app, base: `http://127.0.0.1:${address.port}` };
}

test("raffle unlocks only after completion and remains separate", async (t) => {
  const { app, base } = await start({ raffleSecret: "a".repeat(48) });
  t.after(() => app.close());
  const session = makeSession();
  const draft = { ...session, revision: 1, currentStep: 4, status: "draft", answers: fullAnswers(), answerUpdatedAt: timestamps(fullAnswers()) };
  await fetch(`${base}/api/responses/${session.sessionId}`, { method: "PUT", headers: auth(session.editToken), body: JSON.stringify(draft) });
  let response = await fetch(`${base}/api/raffle-eligibility`, { method: "POST", headers: auth(session.editToken), body: JSON.stringify({ sessionId: session.sessionId }) });
  assert.equal(response.status, 409);
  await fetch(`${base}/api/responses/${session.sessionId}`, { method: "PUT", headers: auth(session.editToken), body: JSON.stringify({ ...draft, revision: 2, status: "completed" }) });
  response = await fetch(`${base}/api/raffle-eligibility`, { method: "POST", headers: auth(session.editToken), body: JSON.stringify({ sessionId: session.sessionId }) });
  assert.equal(response.status, 200);
  const { eligibilityToken } = await response.json();
  response = await fetch(`${base}/api/raffle-entry`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ eligibilityToken, studyIdentifier: "LOS-4711" }) });
  assert.equal(response.status, 201);
  response = await fetch(`${base}/api/raffle-entry`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ eligibilityToken, studyIdentifier: "LOS-4712" }) });
  assert.equal(response.status, 409);
});

async function json(response) {
  const payload = await response.json();
  return { response, payload };
}

function auth(token) {
  return { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };
}

test("PUT upsert, autosave merge, completion and immutable completed records", async (t) => {
  const { app, base } = await start();
  t.after(() => app.close());
  const session = makeSession();

  const firstAnswer = { q1_device: "desktop_laptop" };
  let result = await json(await fetch(`${base}/api/responses/${session.sessionId}`, {
    method: "PUT",
    headers: auth(session.editToken),
    body: JSON.stringify({
      ...session,
      revision: 1,
      currentStep: 1,
      status: "draft",
      answers: firstAnswer,
      answerUpdatedAt: timestamps(firstAnswer),
    }),
  }));
  assert.equal(result.response.status, 200);
  assert.equal(result.payload.response.answers.q1_device, "desktop_laptop");

  result = await json(await fetch(`${base}/api/responses`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(session),
  }));
  assert.equal(result.response.status, 200, "POST remains idempotent after an unload PUT arrived first");
  assert.equal(result.payload.response.revision, 1);

  const secondAnswer = { ...firstAnswer, q2_experience: 2 };
  result = await json(await fetch(`${base}/api/responses/${session.sessionId}`, {
    method: "PUT",
    headers: auth(session.editToken),
    body: JSON.stringify({
      ...session,
      revision: 2,
      currentStep: 2,
      status: "draft",
      answers: secondAnswer,
      answerUpdatedAt: timestamps(secondAnswer, "2026-08-13T10:02:00.000Z"),
    }),
  }));
  assert.equal(result.payload.response.revision, 2);

  const staleTabAnswer = { q3_object_selection_clarity: 5 };
  result = await json(await fetch(`${base}/api/responses/${session.sessionId}`, {
    method: "PUT",
    headers: auth(session.editToken),
    body: JSON.stringify({
      ...session,
      revision: 1,
      currentStep: 1,
      status: "draft",
      answers: staleTabAnswer,
      answerUpdatedAt: timestamps(staleTabAnswer, "2026-08-13T10:03:00.000Z"),
    }),
  }));
  assert.equal(result.payload.response.revision, 2);
  assert.equal(result.payload.response.answers.q2_experience, 2);
  assert.equal(result.payload.response.answers.q3_object_selection_clarity, 5, "new fields from a stale tab are merged safely");

  const completedAnswers = fullAnswers();
  result = await json(await fetch(`${base}/api/responses/${session.sessionId}`, {
    method: "PUT",
    headers: auth(session.editToken),
    body: JSON.stringify({
      ...session,
      revision: 3,
      currentStep: 4,
      status: "completed",
      answers: completedAnswers,
      answerUpdatedAt: timestamps(completedAnswers, "2026-08-13T10:04:00.000Z"),
    }),
  }));
  assert.equal(result.response.status, 200);
  assert.equal(result.payload.response.status, "completed");
  assert.ok(result.payload.response.completedAt);

  const mutation = { ...completedAnswers, q11_overall_score: 0 };
  result = await json(await fetch(`${base}/api/responses/${session.sessionId}`, {
    method: "PUT",
    headers: auth(session.editToken),
    body: JSON.stringify({
      ...session,
      revision: 4,
      currentStep: 4,
      status: "completed",
      answers: mutation,
      answerUpdatedAt: timestamps(mutation, "2026-08-13T10:05:00.000Z"),
    }),
  }));
  assert.equal(result.payload.response.answers.q11_overall_score, 8, "a completed record is immutable");

  const forbidden = await fetch(`${base}/api/responses/${session.sessionId}`, {
    headers: { Authorization: "Bearer ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh123456_-" },
  });
  assert.equal(forbidden.status, 403);
});

test("strict validation rejects unknown answers and incomplete submissions", async (t) => {
  const { app, base } = await start();
  t.after(() => app.close());
  const session = makeSession();

  let response = await fetch(`${base}/api/responses/${session.sessionId}`, {
    method: "PUT",
    headers: auth(session.editToken),
    body: JSON.stringify({
      ...session,
      revision: 1,
      currentStep: 1,
      status: "draft",
      answers: { unknown: "value" },
      answerUpdatedAt: {},
    }),
  });
  assert.equal(response.status, 400);

  response = await fetch(`${base}/api/responses/${session.sessionId}`, {
    method: "PUT",
    headers: auth(session.editToken),
    body: JSON.stringify({
      ...session,
      revision: 1,
      currentStep: 4,
      status: "completed",
      answers: { q1_device: "desktop_laptop" },
      answerUpdatedAt: { q1_device: "2026-08-13T10:01:00.000Z" },
    }),
  });
  assert.equal(response.status, 400);

  response = await fetch(`${base}/api/responses/${session.sessionId}`, {
    method: "PUT",
    headers: auth(session.editToken),
    body: JSON.stringify({
      ...session,
      revision: 1,
      currentStep: 1,
      status: "draft",
      answers: { q11_overall_score: 11 },
      answerUpdatedAt: { q11_overall_score: "2026-08-13T10:01:00.000Z" },
    }),
  });
  assert.equal(response.status, 400);
});

test("PIN gate protects drafts, details, CSV and JSON exports", async (t) => {
  const { app, base } = await start();
  t.after(() => app.close());

  const draft = makeSession();
  await fetch(`${base}/api/responses/${draft.sessionId}`, {
    method: "PUT",
    headers: auth(draft.editToken),
    body: JSON.stringify({
      ...draft,
      revision: 1,
      currentStep: 1,
      status: "draft",
      answers: { q1_device: "vr_headset" },
      answerUpdatedAt: { q1_device: "2026-08-13T10:01:00.000Z" },
    }),
  });

  const completed = makeSession();
  const answers = fullAnswers("=HYPERLINK(\"https://example.invalid\")\nUmlaut: Käse");
  await fetch(`${base}/api/responses/${completed.sessionId}`, {
    method: "PUT",
    headers: auth(completed.editToken),
    body: JSON.stringify({
      ...completed,
      revision: 1,
      currentStep: 4,
      status: "completed",
      answers,
      answerUpdatedAt: timestamps(answers),
    }),
  });

  assert.equal((await fetch(`${base}/api/admin/responses`)).status, 401);
  assert.equal((await fetch(`${base}/api/admin/responses`, { method: "DELETE" })).status, 401);
  assert.equal((await fetch(`${base}/api/admin/export.csv`)).status, 401);

  let login = await fetch(`${base}/api/admin/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pin: "wrong" }),
  });
  assert.equal(login.status, 401);

  login = await fetch(`${base}/api/admin/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pin: "24681012" }),
  });
  assert.equal(login.status, 200);
  const setCookie = login.headers.get("set-cookie");
  assert.match(setCookie, /HttpOnly/i);
  assert.match(setCookie, /SameSite=Strict/i);
  const cookie = setCookie.split(";", 1)[0];

  const list = await json(await fetch(`${base}/api/admin/responses`, { headers: { Cookie: cookie } }));
  assert.equal(list.response.status, 200);
  assert.equal(list.payload.responses.length, 2);
  assert.deepEqual(new Set(list.payload.responses.map((item) => item.status)), new Set(["draft", "completed"]));

  const jsonExport = await json(await fetch(`${base}/api/admin/export.json`, { headers: { Cookie: cookie } }));
  assert.equal(jsonExport.payload.responses.length, 2);

  const csvResponse = await fetch(`${base}/api/admin/export.csv`, { headers: { Cookie: cookie } });
  const csvBytes = Buffer.from(await csvResponse.arrayBuffer());
  assert.deepEqual([...csvBytes.subarray(0, 3)], [0xef, 0xbb, 0xbf], "CSV starts with an UTF-8 BOM");
  const csv = csvBytes.subarray(3).toString("utf8");
  assert.match(csv, /q12_improvement/);
  assert.match(csv, /'=HYPERLINK/, "spreadsheet formulas are neutralized");
  assert.match(csv, /Umlaut: Käse/);

  const deletion = await json(await fetch(`${base}/api/admin/responses`, {
    method: "DELETE",
    headers: { Cookie: cookie },
  }));
  assert.equal(deletion.response.status, 200);
  assert.equal(deletion.payload.deleted, 2);
  const emptyList = await json(await fetch(`${base}/api/admin/responses`, { headers: { Cookie: cookie } }));
  assert.deepEqual(emptyList.payload.responses, []);

  const logout = await fetch(`${base}/api/admin/logout`, { method: "POST", headers: { Cookie: cookie } });
  assert.equal(logout.status, 200);
  assert.equal((await fetch(`${base}/api/admin/responses`, { headers: { Cookie: cookie } })).status, 401);
});

test("PIN login is rate limited", async (t) => {
  const { app, base } = await start({ maxLoginAttempts: 2, loginWindowMs: 60_000 });
  t.after(() => app.close());
  for (let index = 0; index < 2; index += 1) {
    const response = await fetch(`${base}/api/admin/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pin: "wrong" }),
    });
    assert.equal(response.status, 401);
  }
  const limited = await fetch(`${base}/api/admin/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pin: "24681012" }),
  });
  assert.equal(limited.status, 429);
  assert.ok(limited.headers.get("retry-after"));
});

test("SQLite data survives a restart and Brotli Unity files get correct headers", async (t) => {
  const root = mkdtempSync(join(tmpdir(), "survey-server-"));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  const dbPath = join(root, "survey.sqlite");
  const staticDir = join(root, "dist");
  const buildDir = join(staticDir, "BuildOutput", "Build");
  mkdirSync(buildDir, { recursive: true });
  writeFileSync(join(staticDir, "index.html"), "<!doctype html><title>Study</title>");
  writeFileSync(join(buildDir, "sample.wasm.br"), brotliCompressSync(Buffer.from("unity")));

  const session = makeSession();
  let running = await start({ dbPath, staticDir });
  await fetch(`${running.base}/api/responses/${session.sessionId}`, {
    method: "PUT",
    headers: auth(session.editToken),
    body: JSON.stringify({
      ...session,
      revision: 1,
      currentStep: 1,
      status: "draft",
      answers: { q1_device: "desktop_laptop" },
      answerUpdatedAt: { q1_device: "2026-08-13T10:01:00.000Z" },
    }),
  });
  await running.app.close();

  running = await start({ dbPath, staticDir });
  t.after(async () => {
    if (running.app.server.listening) await running.app.close();
  });
  const restored = await json(await fetch(`${running.base}/api/responses/${session.sessionId}`, {
    headers: { Authorization: `Bearer ${session.editToken}` },
  }));
  assert.equal(restored.payload.response.answers.q1_device, "desktop_laptop");

  const raw = await new Promise((resolveRequest, reject) => {
    httpGet(`${running.base}/BuildOutput/Build/sample.wasm.br`, (response) => {
      const chunks = [];
      response.on("data", (chunk) => chunks.push(chunk));
      response.on("end", () => resolveRequest({ headers: response.headers, body: Buffer.concat(chunks) }));
    }).on("error", reject);
  });
  assert.equal(raw.headers["content-encoding"], "br");
  assert.equal(raw.headers["content-type"], "application/wasm");
  assert.deepEqual(raw.body, brotliCompressSync(Buffer.from("unity")));
  await running.app.close();
});
