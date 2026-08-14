const API = Object.freeze({
  login: "/api/admin/login",
  logout: "/api/admin/logout",
  responses: "/api/admin/responses",
  csv: "/api/admin/export.csv",
  json: "/api/admin/export.json",
  raffle: "/api/admin/raffle/export.csv",
  raffleEntries: "/api/admin/raffle",
});

const STATUS = Object.freeze({
  COMPLETED: "completed",
  DRAFT: "draft",
});

const questionLabels = Object.freeze({
  profile_age_group: "Altersgruppe",
  profile_activity_field: "Tätigkeits- oder Studienbereich",
  profile_ai_frequency: "Nutzungshäufigkeit dialogfähiger KI",
  q1_device: "Verwendetes Gerät",
  q1_device_other: "Anderes Gerät",
  q2_experience: "Vorerfahrung mit 3D-Anwendungen oder VR",
  q3_object_selection_clarity: "Klarheit der Objektauswahl",
  q4_object_answer_fit: "Bezug von Antwort, Objekt und Frage",
  q5_handoff_observed: "Weiterleitung wahrgenommen",
  q6_handoff_understandability: "Verständlichkeit der Weiterleitung",
  q7_final_agent_clarity: "Klarheit des antwortenden Agenten",
  q8_object_selection_easy: "Objekte einfach auswählbar",
  q8_answer_fit: "Antworten passten zu Objekten und Fragen",
  q8_agent_responsibility: "Agentenzuständigkeit nachvollziehbar",
  q8_predictability: "Agentenverhalten vorhersehbar",
  q8_guidance_helpful: "Systemhinweise hilfreich",
  q8_overall_ease: "Agenteninteraktion insgesamt einfach",
  q9_error_explanation: "Fehlergrund verständlich erklärt",
  q10_agent_selection_model: "Verständnis der Agentenauswahl",
  q11_overall_score: "Gesamturteil (0–10)",
  q12_improvement: "Wichtigste Verbesserung",
  q13_multi_agent_help: "Mehrere Agenten halfen bei passenden Informationen",
  q14_best_use_case: "Sinnvollster Anwendungsbereich",
});

const valueLabels = Object.freeze({
  "18_24": "18–24", "25_34": "25–34", "35_44": "35–44", "45_54": "45–54",
  "55_64": "55–64", "65_plus": "65 oder älter", no_answer: "Keine Angabe",
  computer_science: "Informatik oder Softwareentwicklung",
  design_hci: "Design, Medien, UX oder HCI", engineering: "Technik oder Ingenieurwesen",
  business: "Wirtschaft, Verwaltung, Marketing oder Vertrieb",
  education_research: "Bildung oder Forschung", food_production: "Lebensmittelwirtschaft oder Produktion",
  other_field: "Anderer Bereich", never: "Nie", less_than_monthly: "Seltener als monatlich",
  monthly: "Ungefähr monatlich", weekly: "Ungefähr wöchentlich", daily: "Täglich oder fast täglich",
  trade_fair: "Virtueller Messestand oder Unternehmenspräsentation",
  product_information: "Produktinformation oder Produktberatung", museum: "Museum oder Ausstellung",
  learning: "Lernen, Schulung oder Weiterbildung", recruiting: "Karriereinformation oder Recruiting",
  customer_service: "Kundenservice", none: "Keiner dieser Bereiche", other_use_case: "Anderer Bereich",
  desktop_laptop: "Desktop-PC oder Laptop",
  vr_headset: "VR-Headset",
  tablet_smartphone: "Tablet oder Smartphone",
  other: "Anderes Gerät",
  yes: "Ja",
  no: "Nein",
  unsure: "Ich bin mir nicht sicher",
  object_and_topic: "Ausgewähltes Objekt und Thema der Frage",
  nearest_agent: "Räumlich nächster Agent",
  first_contacted: "Zuerst angesprochener Agent",
  random: "Zufällige Auswahl",
  unclear: "Nicht erkennbar",
});

const likertQuestions = Object.freeze([
  ["q13_multi_agent_help", "Mehrere Agenten halfen bei passenden Informationen"],
  ["q3_object_selection_clarity", "Objektauswahl klar erkennbar"],
  ["q4_object_answer_fit", "Antwort bezog sich auf Objekt und Frage"],
  ["q6_handoff_understandability", "Weiterleitung verständlich"],
  ["q7_final_agent_clarity", "Antwortender Agent klar erkennbar"],
  ["q8_object_selection_easy", "Objekte einfach auswählbar"],
  ["q8_answer_fit", "Antworten passten zu Objekten und Fragen"],
  ["q8_agent_responsibility", "Agentenzuständigkeit nachvollziehbar"],
  ["q8_predictability", "Agentenverhalten vorhersehbar"],
  ["q8_guidance_helpful", "Systemhinweise hilfreich"],
  ["q8_overall_ease", "Agenteninteraktion insgesamt einfach"],
  ["q9_error_explanation", "Fehlergrund verständlich erklärt"],
]);

const state = {
  authenticated: false,
  loading: false,
  responses: [],
  query: "",
  status: "all",
};

const elements = {
  loginView: document.querySelector("#login-view"),
  dashboardView: document.querySelector("#dashboard-view"),
  loginForm: document.querySelector("#login-form"),
  pin: document.querySelector("#pin"),
  revealPin: document.querySelector("#reveal-pin"),
  loginButton: document.querySelector("#login-button"),
  loginError: document.querySelector("#login-error"),
  logoutButton: document.querySelector("#logout-button"),
  refreshButton: document.querySelector("#refresh-button"),
  exportCsvButton: document.querySelector("#export-csv-button"),
  exportJsonButton: document.querySelector("#export-json-button"),
  exportRaffleButton: document.querySelector("#export-raffle-button"),
  deleteAllButton: document.querySelector("#delete-all-button"),
  statusMessage: document.querySelector("#status-message"),
  totalCount: document.querySelector("#total-count"),
  completedCount: document.querySelector("#completed-count"),
  completedShare: document.querySelector("#completed-share"),
  draftCount: document.querySelector("#draft-count"),
  analysisContent: document.querySelector("#analysis-content"),
  analysisEmpty: document.querySelector("#analysis-empty"),
  analysisSubtitle: document.querySelector("#analysis-subtitle"),
  statusChart: document.querySelector("#status-chart"),
  ageChart: document.querySelector("#age-chart"),
  ageSample: document.querySelector("#age-sample"),
  activityChart: document.querySelector("#activity-chart"),
  activitySample: document.querySelector("#activity-sample"),
  aiChart: document.querySelector("#ai-chart"),
  aiSample: document.querySelector("#ai-sample"),
  useCaseChart: document.querySelector("#use-case-chart"),
  useCaseSample: document.querySelector("#use-case-sample"),
  raffleWinnerCount: document.querySelector("#raffle-winner-count"),
  drawRaffleButton: document.querySelector("#draw-raffle-button"),
  copyRaffleButton: document.querySelector("#copy-raffle-button"),
  raffleStatus: document.querySelector("#raffle-status"),
  raffleWinners: document.querySelector("#raffle-winners"),
  deviceChart: document.querySelector("#device-chart"),
  deviceSample: document.querySelector("#device-sample"),
  experienceChart: document.querySelector("#experience-chart"),
  experienceSample: document.querySelector("#experience-sample"),
  handoffChart: document.querySelector("#handoff-chart"),
  handoffSample: document.querySelector("#handoff-sample"),
  modelChart: document.querySelector("#model-chart"),
  modelSample: document.querySelector("#model-sample"),
  likertChart: document.querySelector("#likert-chart"),
  scoreChart: document.querySelector("#score-chart"),
  scoreAverage: document.querySelector("#score-average"),
  commentsList: document.querySelector("#comments-list"),
  commentsSample: document.querySelector("#comments-sample"),
  lastUpdated: document.querySelector("#last-updated"),
  resultsSummary: document.querySelector("#results-summary"),
  searchInput: document.querySelector("#search-input"),
  statusFilter: document.querySelector("#status-filter"),
  responsesBody: document.querySelector("#responses-body"),
  tableRegion: document.querySelector(".table-region"),
  emptyState: document.querySelector("#empty-state"),
  emptyTitle: document.querySelector("#empty-title"),
  emptyCopy: document.querySelector("#empty-copy"),
  detailDialog: document.querySelector("#detail-dialog"),
  detailTitle: document.querySelector("#detail-title"),
  detailContent: document.querySelector("#detail-content"),
  detailClose: document.querySelector("#detail-close"),
};

const dateTimeFormatter = new Intl.DateTimeFormat("de-DE", {
  dateStyle: "medium",
  timeStyle: "short",
});

function normalizeStatus(response) {
  return response?.status === STATUS.COMPLETED || Boolean(response?.completedAt)
    ? STATUS.COMPLETED
    : STATUS.DRAFT;
}

function getSessionId(response) {
  return String(response?.sessionId ?? response?.id ?? response?._id ?? "Unbekannte Session");
}

function getAnswers(response) {
  return response?.answers && typeof response.answers === "object" && !Array.isArray(response.answers)
    ? response.answers
    : {};
}

function parseDate(value) {
  if (!value) return null;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}

function formatDate(value) {
  const date = parseDate(value);
  return date ? dateTimeFormatter.format(date) : "–";
}

function formatShortId(value) {
  const id = String(value);
  return id.length > 20 ? `${id.slice(0, 8)}…${id.slice(-6)}` : id;
}

function initialsForSession(id) {
  return id.replace(/[^a-zA-Z0-9]/g, "").slice(0, 2).toUpperCase() || "ID";
}

function countAnswers(response) {
  return Object.values(getAnswers(response)).filter((value) => {
    if (Array.isArray(value)) return value.length > 0;
    return value !== "" && value !== null && value !== undefined;
  }).length;
}

function getProgress(response) {
  if (normalizeStatus(response) === STATUS.COMPLETED) return 100;

  const rawProgress = Number(response?.progress);
  if (Number.isFinite(rawProgress)) {
    const normalized = rawProgress <= 1 ? rawProgress * 100 : rawProgress;
    return Math.max(0, Math.min(100, Math.round(normalized)));
  }

  const step = Number(response?.currentStep);
  if (Number.isFinite(step)) {
    return Math.max(0, Math.min(100, Math.round((step / 4) * 100)));
  }

  const answered = countAnswers(response);
  const expectedQuestions = Object.keys(questionLabels).length - 1;
  return Math.max(0, Math.min(99, Math.round((answered / expectedQuestions) * 100)));
}

function formatValue(value, key = "") {
  if (value === null || value === undefined || value === "") return "Nicht beantwortet";
  if (typeof value === "boolean") return value ? "Ja" : "Nein";
  if (Array.isArray(value)) return value.map((item) => formatValue(item, key)).join(", ");
  if (typeof value === "object") return JSON.stringify(value, null, 2);

  const stringValue = String(value);

  if (key === "q2_experience") {
    return ({
      1: "Gar nicht vertraut",
      2: "Wenig vertraut",
      3: "Mäßig vertraut",
      4: "Sehr vertraut",
    })[stringValue] ?? stringValue;
  }

  if (stringValue === "not_experienced") {
    return key === "q9_error_explanation"
      ? "Keine solche Situation erlebt"
      : "Keine Weiterleitung erlebt";
  }

  if (Object.hasOwn(valueLabels, stringValue)) return valueLabels[stringValue];

  const numericValue = Number(stringValue);
  if (Number.isFinite(numericValue) && /^q(?:3|4|6|7|8|9)_/.test(key)) {
    const agreement = {
      1: "stimme überhaupt nicht zu",
      2: "stimme eher nicht zu",
      3: "teils/teils",
      4: "stimme eher zu",
      5: "stimme voll zu",
    }[numericValue];
    return agreement ? `${numericValue} von 5 – ${agreement}` : `${numericValue} von 5`;
  }

  if (key === "q11_overall_score" && Number.isFinite(numericValue)) {
    return `${numericValue} von 10`;
  }

  return stringValue;
}

function getDeviceLabel(response) {
  const answers = getAnswers(response);
  const device = answers.q1_device ?? response?.device;
  if (device === "other" && answers.q1_device_other) return formatValue(answers.q1_device_other);
  return formatValue(device, "q1_device");
}

function createElement(tag, className, textContent) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (textContent !== undefined) element.textContent = textContent;
  return element;
}

function setAuthenticated(authenticated) {
  state.authenticated = authenticated;
  elements.loginView.hidden = authenticated;
  elements.dashboardView.hidden = !authenticated;
  elements.logoutButton.hidden = !authenticated;

  if (authenticated) {
    elements.loginError.hidden = true;
  } else {
    state.responses = [];
    renderDashboard();
  }
}

function setBusy(busy) {
  state.loading = busy;
  [
    elements.refreshButton,
    elements.exportCsvButton,
    elements.exportJsonButton,
  ].forEach((button) => {
    button.disabled = busy;
  });
  elements.refreshButton.textContent = busy ? "Wird geladen…" : "Aktualisieren";
  elements.deleteAllButton.disabled = busy || state.responses.length === 0;
}

function showStatus(message, type = "success") {
  elements.statusMessage.textContent = message;
  elements.statusMessage.classList.toggle("is-error", type === "error");
  elements.statusMessage.hidden = false;
}

function clearStatus() {
  elements.statusMessage.hidden = true;
  elements.statusMessage.textContent = "";
  elements.statusMessage.classList.remove("is-error");
}

function showLoginError(message) {
  elements.loginError.textContent = message;
  elements.loginError.hidden = false;
  elements.pin.setAttribute("aria-invalid", "true");
}

function clearLoginError() {
  elements.loginError.hidden = true;
  elements.loginError.textContent = "";
  elements.pin.removeAttribute("aria-invalid");
}

async function apiFetch(url, options = {}) {
  const headers = new Headers(options.headers ?? {});
  headers.set("Accept", options.accept ?? "application/json");

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: "same-origin",
    cache: "no-store",
  });

  if (response.status === 401 || response.status === 403) {
    const error = new Error("Ihre Sitzung ist abgelaufen. Bitte melden Sie sich erneut an.");
    error.authRequired = true;
    throw error;
  }

  if (!response.ok) {
    let message = `Die Anfrage konnte nicht abgeschlossen werden (${response.status}).`;
    try {
      const payload = await response.json();
      if (typeof payload?.error === "string") message = payload.error;
      if (typeof payload?.message === "string") message = payload.message;
    } catch {
      // The generic status message remains useful for non-JSON errors.
    }
    throw new Error(message);
  }

  return response;
}

function handleAuthRequired(message) {
  setAuthenticated(false);
  clearStatus();
  showLoginError(message);
  elements.pin.value = "";
  elements.pin.focus();
}

function filteredResponses() {
  const query = state.query.trim().toLocaleLowerCase("de-DE");

  return state.responses.filter((response) => {
    const statusMatches = state.status === "all" || normalizeStatus(response) === state.status;
    if (!statusMatches) return false;
    if (!query) return true;

    const haystack = [
      getSessionId(response),
      normalizeStatus(response),
      getDeviceLabel(response),
      ...Object.keys(getAnswers(response)),
      ...Object.values(getAnswers(response)).flatMap((value) => {
        if (typeof value === "object" && value !== null) return JSON.stringify(value);
        return String(value ?? "");
      }),
    ]
      .join(" ")
      .toLocaleLowerCase("de-DE");

    return haystack.includes(query);
  });
}

function sortResponses(responses) {
  return [...responses].sort((left, right) => {
    const leftDate = parseDate(left.updatedAt ?? left.completedAt ?? left.startedAt)?.getTime() ?? 0;
    const rightDate = parseDate(right.updatedAt ?? right.completedAt ?? right.startedAt)?.getTime() ?? 0;
    return rightDate - leftDate;
  });
}

function answerValues(field) {
  return state.responses
    .map((response) => getAnswers(response)[field])
    .filter((value) => value !== undefined && value !== null && value !== "");
}

function formatPercent(count, total) {
  return total ? Math.round((count / total) * 100) : 0;
}

function renderHorizontalBars(container, values, definitions, ariaTitle) {
  const counts = new Map(definitions.map(([value]) => [String(value), 0]));
  values.forEach((value) => {
    const key = String(value);
    if (counts.has(key)) counts.set(key, counts.get(key) + 1);
  });
  const total = values.length;
  const rows = definitions.map(([value, label]) => {
    const count = counts.get(String(value)) ?? 0;
    const percent = formatPercent(count, total);
    const row = createElement("div", "bar-row");
    const meta = createElement("div", "bar-meta");
    meta.append(createElement("span", "bar-label", label), createElement("strong", "bar-value", `${count} · ${percent} %`));
    const track = createElement("div", "bar-track");
    const fill = createElement("span", "bar-fill");
    fill.style.width = `${percent}%`;
    track.append(fill);
    row.append(meta, track);
    return row;
  });
  container.replaceChildren(...rows);
  container.setAttribute("role", "img");
  container.setAttribute(
    "aria-label",
    `${ariaTitle}. ${definitions.map(([value, label]) => `${label}: ${counts.get(String(value)) ?? 0}`).join(", ")}.`,
  );
}

function renderStatusChart() {
  const total = state.responses.length;
  const completed = state.responses.filter((response) => normalizeStatus(response) === STATUS.COMPLETED).length;
  const drafts = total - completed;
  const completedPercent = formatPercent(completed, total);

  const layout = createElement("div", "status-chart-layout");
  const donut = createElement("div", "status-donut");
  donut.style.setProperty("--completed-angle", `${completedPercent * 3.6}deg`);
  donut.setAttribute("role", "img");
  donut.setAttribute("aria-label", `${completed} abgeschlossene und ${drafts} unvollständige Teilnahmen.`);
  const center = createElement("span", "status-donut-center");
  center.append(createElement("strong", "", `${completedPercent} %`), createElement("small", "", "abgeschlossen"));
  donut.append(center);

  const legend = createElement("dl", "status-chart-legend");
  [["Abgeschlossen", completed, "completed"], ["Entwürfe", drafts, "draft"]].forEach(([label, value, className]) => {
    const item = createElement("div", "status-legend-item");
    const term = createElement("dt", "");
    term.append(createElement("i", `status-dot ${className}`), document.createTextNode(label));
    item.append(term, createElement("dd", "", String(value)));
    legend.append(item);
  });
  layout.append(donut, legend);
  elements.statusChart.replaceChildren(layout);
}

function renderLikertChart() {
  const rows = likertQuestions.map(([field, label]) => {
    const values = answerValues(field);
    const numeric = values.filter((value) => Number.isInteger(value) && value >= 1 && value <= 5);
    const notExperienced = values.filter((value) => value === "not_experienced").length;
    const average = numeric.length ? numeric.reduce((sum, value) => sum + value, 0) / numeric.length : null;
    const counts = [1, 2, 3, 4, 5].map((score) => numeric.filter((value) => value === score).length);

    const row = createElement("div", "likert-row");
    const heading = createElement("div", "likert-row-heading");
    heading.append(
      createElement("span", "likert-label", label),
      createElement(
        "span",
        "likert-meta",
        `${average === null ? "Ø –" : `Ø ${average.toLocaleString("de-DE", { minimumFractionDigits: 1, maximumFractionDigits: 1 })}`} · n = ${numeric.length}${notExperienced ? ` · ${notExperienced} ohne Erlebnis` : ""}`,
      ),
    );

    const track = createElement("div", "likert-track");
    track.setAttribute("role", "img");
    track.setAttribute(
      "aria-label",
      `${label}. ${counts.map((count, index) => `Bewertung ${index + 1}: ${count}`).join(", ")}${notExperienced ? `, keine entsprechende Situation: ${notExperienced}` : ""}.`,
    );
    const total = values.length;
    counts.forEach((count, index) => {
      if (!count) return;
      const segment = createElement("span", `likert-segment score-${index + 1}`);
      segment.style.width = `${(count / total) * 100}%`;
      segment.title = `${index + 1}: ${count} (${formatPercent(count, total)} %)`;
      if ((count / total) * 100 >= 9) segment.textContent = String(count);
      track.append(segment);
    });
    if (notExperienced) {
      const segment = createElement("span", "likert-segment score-na");
      segment.style.width = `${(notExperienced / total) * 100}%`;
      segment.title = `Keine entsprechende Situation: ${notExperienced}`;
      if ((notExperienced / total) * 100 >= 9) segment.textContent = String(notExperienced);
      track.append(segment);
    }
    if (!total) track.append(createElement("span", "likert-no-data", "Noch keine Antwort"));
    row.append(heading, track);
    return row;
  });
  elements.likertChart.replaceChildren(...rows);
}

function renderScoreChart() {
  const values = answerValues("q11_overall_score").filter((value) => Number.isInteger(value) && value >= 0 && value <= 10);
  const counts = Array.from({ length: 11 }, (_, score) => values.filter((value) => value === score).length);
  const maximum = Math.max(1, ...counts);
  const average = values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : null;
  elements.scoreAverage.replaceChildren(
    createElement("strong", "", average === null ? "–" : average.toLocaleString("de-DE", { minimumFractionDigits: 1, maximumFractionDigits: 1 })),
    createElement("span", "", `Ø von 10 · n = ${values.length}`),
  );

  const bars = counts.map((count, score) => {
    const item = createElement("div", "score-column");
    const plot = createElement("div", "score-column-plot");
    const bar = createElement("span", "score-column-bar");
    bar.style.height = `${(count / maximum) * 100}%`;
    bar.title = `Bewertung ${score}: ${count}`;
    if (count) bar.append(createElement("strong", "", String(count)));
    plot.append(bar);
    item.append(plot, createElement("span", "score-axis-label", String(score)));
    return item;
  });
  elements.scoreChart.replaceChildren(...bars);
  elements.scoreChart.setAttribute("role", "img");
  elements.scoreChart.setAttribute("aria-label", `Gesamturteil von 0 bis 10. ${counts.map((count, score) => `${score}: ${count}`).join(", ")}.`);
}

function renderComments() {
  const comments = answerValues("q12_improvement")
    .map((value) => String(value).trim())
    .filter(Boolean);
  elements.commentsSample.textContent = `n = ${comments.length}`;
  if (!comments.length) {
    elements.commentsList.replaceChildren(createElement("p", "no-chart-data", "Noch keine Verbesserungsvorschläge vorhanden."));
    return;
  }
  const list = createElement("ol", "comments-items");
  comments.forEach((comment) => list.append(createElement("li", "", comment)));
  elements.commentsList.replaceChildren(list);
}

function renderAnalysis() {
  const total = state.responses.length;
  elements.analysisEmpty.hidden = total > 0;
  elements.analysisContent.hidden = total === 0;
  elements.analysisSubtitle.textContent = total
    ? `Berücksichtigt alle ${total} gespeicherten ${total === 1 ? "Teilnahme" : "Teilnahmen"}, einschließlich Entwürfen. Die Stichprobengröße n wird je Frage ausgewiesen.`
    : "Berücksichtigt alle bisher gespeicherten Antworten, einschließlich Entwürfen.";
  if (!total) return;

  renderStatusChart();

  const categoricalCharts = [
    ["profile_age_group", elements.ageChart, elements.ageSample, [["18_24", "18–24"], ["25_34", "25–34"], ["35_44", "35–44"], ["45_54", "45–54"], ["55_64", "55–64"], ["65_plus", "65 oder älter"], ["no_answer", "Keine Angabe"]], "Altersgruppen"],
    ["profile_activity_field", elements.activityChart, elements.activitySample, [["computer_science", "Informatik/Software"], ["design_hci", "Design/Medien/UX/HCI"], ["engineering", "Technik/Ingenieurwesen"], ["business", "Wirtschaft/Verwaltung/Vertrieb"], ["education_research", "Bildung/Forschung"], ["food_production", "Lebensmittel/Produktion"], ["other_field", "Anderer Bereich"], ["no_answer", "Keine Angabe"]], "Tätigkeitsbereiche"],
    ["profile_ai_frequency", elements.aiChart, elements.aiSample, [["never", "Nie"], ["less_than_monthly", "Seltener als monatlich"], ["monthly", "Monatlich"], ["weekly", "Wöchentlich"], ["daily", "Täglich/fast täglich"]], "KI-Nutzung"],
  ];
  categoricalCharts.forEach(([field, chart, sample, options, title]) => {
    const values = answerValues(field);
    sample.textContent = `n = ${values.length}`;
    renderHorizontalBars(chart, values, options, title);
  });

  const useCaseResponses = answerValues("q14_best_use_case");
  const useCaseValues = useCaseResponses.flatMap((value) => Array.isArray(value) ? value : [value]);
  elements.useCaseSample.textContent = `n = ${useCaseResponses.length} · ${useCaseValues.length} Nennungen`;
  renderHorizontalBars(elements.useCaseChart, useCaseValues, [
    ["trade_fair", "Messestand/Unternehmenspräsentation"], ["product_information", "Produktinformation/-beratung"],
    ["museum", "Museum/Ausstellung"], ["learning", "Lernen/Schulung/Weiterbildung"],
    ["recruiting", "Karriere/Recruiting"], ["customer_service", "Kundenservice"],
    ["none", "Keiner dieser Bereiche"], ["other_use_case", "Anderer Bereich"],
  ], "Anwendungsbereiche (Mehrfachauswahl)");

  const deviceValues = answerValues("q1_device");
  elements.deviceSample.textContent = `n = ${deviceValues.length}`;
  renderHorizontalBars(elements.deviceChart, deviceValues, [
    ["desktop_laptop", "Desktop/Laptop"],
    ["vr_headset", "VR-Headset"],
    ["tablet_smartphone", "Tablet/Smartphone"],
    ["other", "Anderes Gerät"],
  ], "Verwendete Geräte");

  const experienceValues = answerValues("q2_experience");
  elements.experienceSample.textContent = `n = ${experienceValues.length}`;
  renderHorizontalBars(elements.experienceChart, experienceValues, [
    [1, "Gar nicht vertraut"],
    [2, "Wenig vertraut"],
    [3, "Mäßig vertraut"],
    [4, "Sehr vertraut"],
  ], "Vorerfahrung mit 3D-Anwendungen oder VR");

  const handoffValues = answerValues("q5_handoff_observed");
  elements.handoffSample.textContent = `n = ${handoffValues.length}`;
  renderHorizontalBars(elements.handoffChart, handoffValues, [
    ["yes", "Ja"],
    ["no", "Nein"],
    ["unsure", "Nicht sicher"],
  ], "Wahrnehmung der Weiterleitung");

  const modelValues = answerValues("q10_agent_selection_model");
  elements.modelSample.textContent = `n = ${modelValues.length}`;
  renderHorizontalBars(elements.modelChart, modelValues, [
    ["object_and_topic", "Objekt und Fragenthema"],
    ["nearest_agent", "Räumlich nächster Agent"],
    ["first_contacted", "Zuerst angesprochener Agent"],
    ["random", "Zufällige Auswahl"],
    ["unclear", "Nicht erkennbar"],
  ], "Verständnis der Agentenauswahl");

  renderLikertChart();
  renderScoreChart();
  renderComments();
}

function secureRandomIndex(maxExclusive) {
  const limit = Math.floor(0x100000000 / maxExclusive) * maxExclusive;
  const buffer = new Uint32Array(1);
  do crypto.getRandomValues(buffer); while (buffer[0] >= limit);
  return buffer[0] % maxExclusive;
}

async function drawRaffle() {
  elements.drawRaffleButton.disabled = true;
  elements.raffleStatus.textContent = "Kennungen werden geladen …";
  try {
    const response = await apiFetch(API.raffleEntries, { accept: "application/json" });
    const { identifiers = [] } = await response.json();
    const requested = Number.parseInt(elements.raffleWinnerCount.value, 10);
    if (!Number.isInteger(requested) || requested < 1) throw new Error("Bitte geben Sie mindestens eine Person an.");
    if (!identifiers.length) throw new Error("Es liegen noch keine Studierendenkennungen für die Verlosung vor.");
    if (requested > identifiers.length) throw new Error(`Es können höchstens ${identifiers.length} Kennungen gezogen werden.`);
    const pool = [...identifiers];
    for (let index = pool.length - 1; index > 0; index -= 1) {
      const randomIndex = secureRandomIndex(index + 1);
      [pool[index], pool[randomIndex]] = [pool[randomIndex], pool[index]];
    }
    const winners = pool.slice(0, requested);
    elements.raffleWinners.replaceChildren(...winners.map((identifier) => createElement("li", "", identifier)));
    elements.raffleStatus.textContent = `${requested} von ${identifiers.length} Kennungen zufällig gezogen.`;
    elements.copyRaffleButton.hidden = false;
  } catch (error) {
    elements.raffleWinners.replaceChildren();
    elements.copyRaffleButton.hidden = true;
    elements.raffleStatus.textContent = error.message || "Die Ziehung ist fehlgeschlagen.";
  } finally { elements.drawRaffleButton.disabled = false; }
}

async function copyRaffleResult() {
  const values = [...elements.raffleWinners.children].map((item, index) => `${index + 1}. ${item.textContent}`);
  await navigator.clipboard.writeText(values.join("\n"));
  elements.raffleStatus.textContent = "Ziehung wurde in die Zwischenablage kopiert.";
}

function renderSummary() {
  const total = state.responses.length;
  const completed = state.responses.filter((response) => normalizeStatus(response) === STATUS.COMPLETED).length;
  const draft = total - completed;
  const share = total ? Math.round((completed / total) * 100) : 0;

  elements.totalCount.textContent = String(total);
  elements.completedCount.textContent = String(completed);
  elements.draftCount.textContent = String(draft);
  elements.completedShare.textContent = total
    ? `${share} % aller Teilnahmen`
    : "vollständig beantwortet";
  elements.deleteAllButton.disabled = state.loading || total === 0;
}

function renderEmptyState(filteredCount) {
  const hasResponses = state.responses.length > 0;
  const hasFilter = Boolean(state.query.trim()) || state.status !== "all";
  const showEmpty = filteredCount === 0;

  elements.emptyState.hidden = !showEmpty;
  elements.tableRegion.hidden = showEmpty;

  if (!showEmpty) return;

  if (hasResponses && hasFilter) {
    elements.emptyTitle.textContent = "Keine passenden Antworten";
    elements.emptyCopy.textContent = "Passen Sie die Suche oder den Statusfilter an.";
  } else {
    elements.emptyTitle.textContent = "Keine Antworten vorhanden";
    elements.emptyCopy.textContent = "Sobald Antworten gespeichert wurden, erscheinen sie hier.";
  }
}

function buildResponseRow(response) {
  const row = document.createElement("tr");
  const sessionId = getSessionId(response);
  const status = normalizeStatus(response);
  const progress = getProgress(response);
  const answerCount = countAnswers(response);

  const sessionTd = document.createElement("td");
  const sessionCell = createElement("div", "session-cell");
  sessionCell.append(createElement("span", "session-avatar", initialsForSession(sessionId)));
  const sessionText = document.createElement("span");
  const idText = createElement("span", "session-id", formatShortId(sessionId));
  idText.title = sessionId;
  sessionText.append(idText, createElement("span", "session-subline", `${answerCount} Antworten`));
  sessionCell.append(sessionText);
  sessionTd.append(sessionCell);

  const statusTd = document.createElement("td");
  statusTd.append(
    createElement(
      "span",
      `status-badge ${status}`,
      status === STATUS.COMPLETED ? "Abgeschlossen" : "Entwurf",
    ),
  );

  const deviceTd = createElement("td", "", getDeviceLabel(response));

  const progressTd = document.createElement("td");
  const progressCell = createElement("div", "progress-cell");
  const progressTrack = createElement("span", "progress-track");
  const progressFill = createElement("span", "progress-fill");
  progressFill.style.width = `${progress}%`;
  progressTrack.append(progressFill);
  progressCell.append(progressTrack, createElement("span", "", `${progress} %`));
  progressTd.append(progressCell);

  const startedTd = createElement("td", "", formatDate(response.startedAt ?? response.createdAt));
  const updatedTd = createElement(
    "td",
    "",
    formatDate(response.updatedAt ?? response.completedAt ?? response.startedAt ?? response.createdAt),
  );

  const actionTd = document.createElement("td");
  const detailsButton = createElement("button", "details-button", "Ansehen");
  detailsButton.type = "button";
  detailsButton.dataset.sessionId = sessionId;
  detailsButton.setAttribute("aria-label", `Antworten der Session ${sessionId} ansehen`);
  actionTd.append(detailsButton);

  row.append(sessionTd, statusTd, deviceTd, progressTd, startedTd, updatedTd, actionTd);
  return row;
}

function renderTable() {
  const responses = sortResponses(filteredResponses());
  elements.responsesBody.replaceChildren(...responses.map(buildResponseRow));

  const total = state.responses.length;
  const shown = responses.length;
  elements.resultsSummary.textContent = total === shown
    ? `${total} ${total === 1 ? "Teilnahme" : "Teilnahmen"}`
    : `${shown} von ${total} Teilnahmen`;

  renderEmptyState(shown);
}

function renderDashboard() {
  renderSummary();
  renderAnalysis();
  renderTable();
}

function appendDefinition(container, label, value, className = "") {
  const item = createElement("div", className);
  const term = createElement("dt", "", label);
  const definition = createElement("dd", "", value);
  item.append(term, definition);
  container.append(item);
}

function openDetails(sessionId) {
  const response = state.responses.find((item) => getSessionId(item) === sessionId);
  if (!response) {
    showStatus("Die ausgewählte Teilnahme wurde nicht gefunden.", "error");
    return;
  }

  const status = normalizeStatus(response);
  const answers = getAnswers(response);
  elements.detailTitle.textContent = `Session ${formatShortId(sessionId)}`;
  elements.detailContent.replaceChildren();

  const overview = createElement("dl", "detail-overview");
  appendDefinition(overview, "Session-ID", sessionId, "detail-meta");
  appendDefinition(
    overview,
    "Status",
    status === STATUS.COMPLETED ? "Abgeschlossen" : "Entwurf",
    "detail-meta",
  );
  appendDefinition(overview, "Begonnen", formatDate(response.startedAt ?? response.createdAt), "detail-meta");
  appendDefinition(
    overview,
    "Zuletzt gespeichert",
    formatDate(response.updatedAt ?? response.completedAt ?? response.startedAt),
    "detail-meta",
  );
  if (response.completedAt) {
    appendDefinition(overview, "Abgeschlossen", formatDate(response.completedAt), "detail-meta");
  }
  appendDefinition(overview, "Fortschritt", `${getProgress(response)} %`, "detail-meta");
  if (Number.isFinite(Number(response.currentStep))) {
    appendDefinition(overview, "Aktueller Schritt", `${response.currentStep} von 4`, "detail-meta");
  }
  if (Number.isFinite(Number(response.revision))) {
    appendDefinition(overview, "Datenrevision", String(response.revision), "detail-meta");
  }
  if (Array.isArray(response.taskCodes) && response.taskCodes.length) {
    appendDefinition(overview, "Aufgabencodes", response.taskCodes.join(", "), "detail-meta");
  }
  elements.detailContent.append(overview);

  const section = createElement("section", "detail-section");
  section.append(createElement("h3", "", "Fragebogenantworten"));
  const answerList = createElement("dl", "answer-list");

  const knownKeys = Object.keys(questionLabels).filter((key) => Object.hasOwn(answers, key));
  const additionalKeys = Object.keys(answers).filter((key) => !Object.hasOwn(questionLabels, key));
  const orderedKeys = [...knownKeys, ...additionalKeys];

  if (orderedKeys.length === 0) {
    answerList.append(createElement("p", "", "Für diese Teilnahme wurden noch keine Antworten gespeichert."));
  } else {
    orderedKeys.forEach((key) => {
      const isWide = key === "q12_improvement" || typeof answers[key] === "object";
      appendDefinition(
        answerList,
        questionLabels[key] ?? key,
        formatValue(answers[key], key),
        `answer-item${isWide ? " wide" : ""}`,
      );
    });
  }

  section.append(answerList);
  elements.detailContent.append(section);

  const rawDetails = createElement("details", "raw-details");
  rawDetails.append(createElement("summary", "", "Technische Rohdaten anzeigen"));
  rawDetails.append(createElement("pre", "", JSON.stringify(response, null, 2)));
  elements.detailContent.append(rawDetails);

  elements.detailDialog.showModal();
}

async function loadResponses({ announce = false, silentAuth = false } = {}) {
  if (state.loading) return;
  setBusy(true);
  clearStatus();

  try {
    const response = await apiFetch(API.responses);
    const payload = await response.json();
    state.responses = Array.isArray(payload?.responses) ? payload.responses : [];
    setAuthenticated(true);
    renderDashboard();
    elements.lastUpdated.textContent = `Zuletzt aktualisiert: ${dateTimeFormatter.format(new Date())}`;
    if (announce) showStatus("Die Antworten wurden aktualisiert.");
  } catch (error) {
    if (error.authRequired) {
      if (silentAuth) {
        setAuthenticated(false);
      } else {
        handleAuthRequired(error.message);
      }
    } else if (state.authenticated) {
      showStatus(error.message || "Die Antworten konnten nicht geladen werden.", "error");
    } else {
      setAuthenticated(false);
    }
  } finally {
    setBusy(false);
  }
}

async function deleteAllResponses() {
  const count = state.responses.length;
  if (!count) return;
  const confirmation = window.prompt(
    `Dadurch werden alle ${count} gespeicherten Teilnahmen unwiderruflich gelöscht. Geben Sie zum Bestätigen LÖSCHEN ein.`,
  );
  if (confirmation?.trim().toLocaleUpperCase("de-DE") !== "LÖSCHEN") return;

  const originalLabel = elements.deleteAllButton.textContent;
  setBusy(true);
  elements.deleteAllButton.textContent = "Wird gelöscht…";
  clearStatus();
  try {
    const response = await apiFetch(API.responses, { method: "DELETE" });
    const payload = await response.json();
    const deleted = Number(payload?.deleted ?? count);
    state.responses = [];
    state.query = "";
    state.status = "all";
    elements.searchInput.value = "";
    elements.statusFilter.value = "all";
    renderDashboard();
    elements.lastUpdated.textContent = `Zuletzt aktualisiert: ${dateTimeFormatter.format(new Date())}`;
    showStatus(`${deleted} ${deleted === 1 ? "Teilnahme wurde" : "Teilnahmen wurden"} vollständig gelöscht.`);
  } catch (error) {
    if (error.authRequired) {
      handleAuthRequired(error.message);
    } else {
      showStatus(error.message || "Die Antworten konnten nicht gelöscht werden.", "error");
    }
  } finally {
    setBusy(false);
    elements.deleteAllButton.textContent = originalLabel;
  }
}

async function login(event) {
  event.preventDefault();
  clearLoginError();
  const pin = elements.pin.value.trim();

  if (!pin) {
    showLoginError("Bitte geben Sie die Verwaltungs-PIN ein.");
    elements.pin.focus();
    return;
  }

  elements.loginButton.disabled = true;
  elements.loginButton.textContent = "Anmeldung läuft…";

  try {
    const response = await fetch(API.login, {
      method: "POST",
      credentials: "same-origin",
      cache: "no-store",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ pin }),
    });

    if (!response.ok) {
      if (response.status === 401 || response.status === 403) {
        throw new Error("Die PIN ist nicht korrekt.");
      }

      let message = "Die Anmeldung konnte nicht abgeschlossen werden.";
      try {
        const payload = await response.json();
        message = payload?.error ?? payload?.message ?? message;
      } catch {
        // Keep the generic message for non-JSON server errors.
      }
      throw new Error(message);
    }

    elements.pin.value = "";
    elements.pin.type = "password";
    elements.revealPin.textContent = "Anzeigen";
    elements.revealPin.setAttribute("aria-pressed", "false");
    setAuthenticated(true);
    await loadResponses();
  } catch (error) {
    setAuthenticated(false);
    showLoginError(error.message || "Die Anmeldung konnte nicht abgeschlossen werden.");
    elements.pin.select();
  } finally {
    elements.loginButton.disabled = false;
    elements.loginButton.textContent = "Anmelden";
  }
}

async function logout() {
  elements.logoutButton.disabled = true;
  try {
    const response = await fetch(API.logout, {
      method: "POST",
      credentials: "same-origin",
      cache: "no-store",
      headers: { Accept: "application/json" },
    });

    if (!response.ok && response.status !== 401 && response.status !== 403) {
      throw new Error(`Die Abmeldung konnte nicht abgeschlossen werden (${response.status}).`);
    }

    if (elements.detailDialog.open) elements.detailDialog.close();
    setAuthenticated(false);
    elements.pin.value = "";
    elements.pin.focus();
  } catch (error) {
    showStatus(error.message || "Die Abmeldung konnte nicht abgeschlossen werden.", "error");
  } finally {
    elements.logoutButton.disabled = false;
  }
}

function filenameFromResponse(response, fallback) {
  const disposition = response.headers.get("Content-Disposition") ?? "";
  const encoded = disposition.match(/filename\*=UTF-8''([^;]+)/i)?.[1];
  if (encoded) {
    try {
      return decodeURIComponent(encoded.replace(/["']/g, ""));
    } catch {
      // Fall back to the regular filename or the local timestamp.
    }
  }

  const regular = disposition.match(/filename="?([^";]+)"?/i)?.[1];
  return regular || fallback;
}

function localExportFilename(extension) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
  return `fragebogen-antworten-${timestamp}.${extension}`;
}

async function downloadExport(format) {
  const isCsv = format === "csv";
  const button = isCsv ? elements.exportCsvButton : elements.exportJsonButton;
  const endpoint = isCsv ? API.csv : API.json;
  const originalLabel = button.textContent;

  button.disabled = true;
  button.textContent = "Export wird erstellt…";
  clearStatus();

  try {
    const response = await apiFetch(endpoint, {
      accept: isCsv ? "text/csv, application/octet-stream" : "application/json, application/octet-stream",
    });
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filenameFromResponse(response, localExportFilename(format));
    anchor.hidden = true;
    document.body.append(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    showStatus(`${isCsv ? "CSV" : "JSON"}-Export wurde heruntergeladen.`);
  } catch (error) {
    if (error.authRequired) {
      handleAuthRequired(error.message);
    } else {
      showStatus(error.message || "Der Export konnte nicht erstellt werden.", "error");
    }
  } finally {
    button.disabled = false;
    button.textContent = originalLabel;
  }
}

async function downloadRaffleExport() {
  const button = elements.exportRaffleButton;
  const originalLabel = button.textContent;
  button.disabled = true;
  button.textContent = "Export wird erstellt…";
  try {
    const response = await apiFetch(API.raffle, { accept: "text/csv, application/octet-stream" });
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filenameFromResponse(response, "verlosung-kennungen.csv");
    document.body.append(anchor); anchor.click(); anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    showStatus("Studierendenkennungen wurden getrennt als CSV heruntergeladen.");
  } catch (error) {
    if (error.authRequired) handleAuthRequired(error.message);
    else showStatus(error.message || "Der Export konnte nicht erstellt werden.", "error");
  } finally {
    button.disabled = false;
    button.textContent = originalLabel;
  }
}

function togglePinVisibility() {
  const reveal = elements.pin.type === "password";
  elements.pin.type = reveal ? "text" : "password";
  elements.revealPin.textContent = reveal ? "Ausblenden" : "Anzeigen";
  elements.revealPin.setAttribute("aria-pressed", String(reveal));
  elements.pin.focus({ preventScroll: true });
}

function initializeEvents() {
  elements.loginForm.addEventListener("submit", login);
  elements.pin.addEventListener("input", clearLoginError);
  elements.revealPin.addEventListener("click", togglePinVisibility);
  elements.logoutButton.addEventListener("click", logout);
  elements.refreshButton.addEventListener("click", () => loadResponses({ announce: true }));
  elements.exportCsvButton.addEventListener("click", () => downloadExport("csv"));
  elements.exportJsonButton.addEventListener("click", () => downloadExport("json"));
  elements.exportRaffleButton.addEventListener("click", downloadRaffleExport);
  elements.drawRaffleButton.addEventListener("click", drawRaffle);
  elements.copyRaffleButton.addEventListener("click", copyRaffleResult);
  elements.deleteAllButton.addEventListener("click", deleteAllResponses);

  elements.searchInput.addEventListener("input", (event) => {
    state.query = event.target.value;
    renderTable();
  });

  elements.statusFilter.addEventListener("change", (event) => {
    state.status = event.target.value;
    renderTable();
  });

  elements.responsesBody.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-session-id]");
    if (button) openDetails(button.dataset.sessionId);
  });

  elements.detailClose.addEventListener("click", () => elements.detailDialog.close());
  elements.detailDialog.addEventListener("click", (event) => {
    if (event.target === elements.detailDialog) elements.detailDialog.close();
  });
}

async function initialize() {
  initializeEvents();
  setAuthenticated(false);
  await loadResponses({ silentAuth: true });
  if (!state.authenticated) elements.pin.focus();
}

initialize();
