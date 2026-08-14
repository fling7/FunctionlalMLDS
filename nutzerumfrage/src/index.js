import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import ReactDOM from "react-dom/client";
import UnityLoader from "./UnityLoader";
import "./survey.css";

const STORAGE_KEY = "kaesesteinpilz.survey.session.v1";
const TASK_CODES = ["TASK_OBJECT_PRODUCT", "TASK_HANDOFF_RECEPTION_PRODUCT"];
const LIKERT = [
  [1, "stimme überhaupt nicht zu"],
  [2, "stimme eher nicht zu"],
  [3, "teils/teils"],
  [4, "stimme eher zu"],
  [5, "stimme vollständig zu"],
];

const STEP_FIELDS = {
  1: ["profile_age_group", "profile_activity_field", "profile_ai_frequency", "q1_device", "q2_experience"],
  2: ["q3_object_selection_clarity", "q4_object_answer_fit"],
  3: [
    "q5_handoff_observed",
    "q6_handoff_understandability",
    "q7_final_agent_clarity",
  ],
  4: [
    "q8_object_selection_easy",
    "q8_answer_fit",
    "q8_agent_responsibility",
    "q8_predictability",
    "q8_guidance_helpful",
    "q8_overall_ease",
    "q9_error_explanation",
    "q10_agent_selection_model",
    "q11_overall_score",
    "q13_multi_agent_help",
    "q14_best_use_case",
  ],
};

const Q8_ITEMS = [
  ["q8_object_selection_easy", "Die Objekte im virtuellen Raum ließen sich einfach auswählen."],
  ["q8_answer_fit", "Die Antworten passten zu den jeweils ausgewählten Objekten und meinen Fragen."],
  ["q8_agent_responsibility", "Es war für mich nachvollziehbar, welcher Agent für eine Frage zuständig war."],
  ["q8_predictability", "Das Verhalten der verschiedenen Agenten war für mich vorhersehbar."],
  ["q8_guidance_helpful", "Die Hinweise des Systems zur Objektauswahl und zu Weiterleitungen halfen mir bei der Orientierung."],
  ["q8_overall_ease", "Die Interaktion mit den virtuellen Agenten war insgesamt einfach."],
];

function randomToken() {
  const bytes = crypto.getRandomValues(new Uint8Array(32));
  let binary = "";
  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  return btoa(binary).replaceAll("+", "-").replaceAll("/", "_").replace(/=+$/, "");
}

function createSession() {
  const now = new Date().toISOString();
  return {
    schemaVersion: 1,
    sessionId: crypto.randomUUID(),
    editToken: randomToken(),
    status: "draft",
    currentStep: 1,
    taskCodes: TASK_CODES,
    revision: 0,
    startedAt: now,
    updatedAt: now,
    completedAt: null,
    answers: {},
    answerUpdatedAt: {},
  };
}

function readSession() {
  try {
    const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY));
    if (
      parsed?.schemaVersion === 1 &&
      typeof parsed.sessionId === "string" &&
      typeof parsed.editToken === "string"
    ) {
      return {
        ...parsed,
        taskCodes: TASK_CODES,
        answers: parsed.answers ?? {},
        answerUpdatedAt: parsed.answerUpdatedAt ?? {},
      };
    }
  } catch {
    // A fresh anonymous session is created below.
  }
  const fresh = createSession();
  localStorage.setItem(STORAGE_KEY, JSON.stringify(fresh));
  return fresh;
}

function serverRecord(payload) {
  return payload?.response ?? payload?.session ?? payload;
}

async function parseApiResponse(response) {
  let payload = {};
  try {
    payload = await response.json();
  } catch {
    // The status text below remains useful when a proxy returns no JSON.
  }
  if (!response.ok) {
    const error = new Error(payload.error ?? `Speichern fehlgeschlagen (${response.status})`);
    error.status = response.status;
    error.payload = payload;
    throw error;
  }
  return payload;
}

function useSurveySession() {
  const initial = useMemo(readSession, []);
  const [record, setRecord] = useState(initial);
  const [saveState, setSaveState] = useState("local");
  const [saveMessage, setSaveMessage] = useState("Lokal gesichert");
  const recordRef = useRef(initial);
  // A reload must also retry a locally completed record whose last upload failed.
  const pendingRef = useRef(initial);
  const timerRef = useRef(null);
  const retryRef = useRef(null);
  const chainRef = useRef(Promise.resolve());
  const mountedRef = useRef(true);
  const persistedRevisionRef = useRef(-1);

  const classifySyncError = useCallback((error) => {
    if (!error?.status || error.status >= 500 || error.status === 408 || error.status === 429) {
      return "retry";
    }
    return "permanent";
  }, []);

  const storeLocal = useCallback((next) => {
    recordRef.current = next;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    if (mountedRef.current) setRecord(next);
  }, []);

  const applyServerRecord = useCallback((remote) => {
    const local = recordRef.current;
    if (!remote || remote.sessionId !== local.sessionId) return;
    if ((remote.revision ?? -1) < (local.revision ?? 0)) return;

    const merged = {
      ...local,
      ...remote,
      editToken: local.editToken,
      taskCodes: remote.taskCodes ?? local.taskCodes,
      answers: remote.answers ?? local.answers,
      answerUpdatedAt: remote.answerUpdatedAt ?? local.answerUpdatedAt,
    };
    storeLocal(merged);
  }, [storeLocal]);

  const syncSnapshot = useCallback(async (snapshot) => {
    if (mountedRef.current) {
      setSaveState("saving");
      setSaveMessage("Wird gespeichert …");
    }

    const createPayload = await parseApiResponse(
      await fetch("/api/responses", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sessionId: snapshot.sessionId,
          editToken: snapshot.editToken,
          schemaVersion: snapshot.schemaVersion,
          startedAt: snapshot.startedAt,
          taskCodes: snapshot.taskCodes,
        }),
      }),
    );

    const remote = serverRecord(createPayload);
    if (remote?.status === "completed" || (remote?.revision ?? 0) > snapshot.revision) {
      persistedRevisionRef.current = Math.max(
        persistedRevisionRef.current,
        Number(remote?.revision ?? 0),
      );
      applyServerRecord(remote);
      if (
        mountedRef.current &&
        !pendingRef.current &&
        recordRef.current.revision <= (remote.revision ?? snapshot.revision)
      ) {
        setSaveState("saved");
        setSaveMessage("Gespeichert");
      }
      return remote;
    }

    const putPayload = await parseApiResponse(
      await fetch(`/api/responses/${encodeURIComponent(snapshot.sessionId)}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${snapshot.editToken}`,
        },
        body: JSON.stringify({
          revision: snapshot.revision,
          currentStep: snapshot.currentStep,
          status: snapshot.status,
          answers: snapshot.answers,
          answerUpdatedAt: snapshot.answerUpdatedAt,
          startedAt: snapshot.startedAt,
          schemaVersion: snapshot.schemaVersion,
          taskCodes: snapshot.taskCodes,
        }),
      }),
    );

    const persisted = serverRecord(putPayload);
    persistedRevisionRef.current = Math.max(
      persistedRevisionRef.current,
      Number(persisted?.revision ?? snapshot.revision),
    );
    applyServerRecord(persisted);
    if (
      mountedRef.current &&
      !pendingRef.current &&
      recordRef.current.revision <= snapshot.revision
    ) {
      setSaveState("saved");
      setSaveMessage("Gespeichert");
    }
    return persisted;
  }, [applyServerRecord]);

  const flush = useCallback(async () => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
    const snapshot = pendingRef.current;
    if (!snapshot) return chainRef.current;
    pendingRef.current = null;

    const operation = chainRef.current
      .catch(() => undefined)
      .then(() => syncSnapshot(snapshot));
    chainRef.current = operation;

    try {
      const result = await operation;
      if (pendingRef.current && !timerRef.current) {
        timerRef.current = setTimeout(() => {
          timerRef.current = null;
          flush().catch(() => undefined);
        }, 80);
      }
      return result;
    } catch (error) {
      const latest = recordRef.current;
      if (!pendingRef.current || pendingRef.current.revision < latest.revision) {
        pendingRef.current = latest;
      }
      if (mountedRef.current) {
        const retryable = classifySyncError(error) === "retry";
        setSaveState(retryable ? "offline" : "error");
        setSaveMessage(
          retryable
            ? "Lokal gesichert · Übertragung ausstehend"
            : "Lokal gesichert · Bitte Studienleitung informieren",
        );
      }
      if (classifySyncError(error) === "retry") {
        clearTimeout(retryRef.current);
        retryRef.current = setTimeout(() => {
          retryRef.current = null;
          flush().catch(() => undefined);
        }, 5000);
      }
      throw error;
    }
  }, [classifySyncError, syncSnapshot]);

  const queue = useCallback((next, delay = 80) => {
    storeLocal(next);
    pendingRef.current = next;
    if (mountedRef.current) {
      setSaveState("saving");
      setSaveMessage("Wird gespeichert …");
    }
    clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      timerRef.current = null;
      flush().catch(() => undefined);
    }, delay);
  }, [flush, storeLocal]);

  const updateAnswer = useCallback((key, value, delay = 80) => {
    const current = recordRef.current;
    if (current.status === "completed") return;
    const now = new Date().toISOString();
    const next = {
      ...current,
      revision: current.revision + 1,
      updatedAt: now,
      answers: { ...current.answers, [key]: value },
      answerUpdatedAt: { ...current.answerUpdatedAt, [key]: now },
    };

    if (key === "q1_device" && value !== "other" && "q1_device_other" in next.answers) {
      delete next.answers.q1_device_other;
      delete next.answerUpdatedAt.q1_device_other;
    }
    queue(next, delay);
  }, [queue]);

  const moveToStep = useCallback((step) => {
    const current = recordRef.current;
    const now = new Date().toISOString();
    const next = {
      ...current,
      currentStep: step,
      revision: current.revision + 1,
      updatedAt: now,
    };
    queue(next, 0);
    return next;
  }, [queue]);

  const complete = useCallback(async () => {
    const current = recordRef.current;
    if (current.status === "completed") return current;
    const now = new Date().toISOString();
    const next = {
      ...current,
      status: "completed",
      completedAt: now,
      updatedAt: now,
      revision: current.revision + 1,
    };
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
    storeLocal(next);
    pendingRef.current = next;
    if (mountedRef.current) {
      setSaveState("saving");
      setSaveMessage("Wird gespeichert …");
    }
    try {
      await flush();
    } catch {
      // The completed record remains locally queued and retries automatically.
    }
    return next;
  }, [flush, storeLocal]);

  const startNew = useCallback(() => {
    clearTimeout(timerRef.current);
    clearTimeout(retryRef.current);
    const fresh = createSession();
    pendingRef.current = fresh;
    storeLocal(fresh);
    setSaveState("local");
    setSaveMessage("Lokal gesichert");
    timerRef.current = setTimeout(() => {
      timerRef.current = null;
      flush().catch(() => undefined);
    }, 0);
  }, [flush, storeLocal]);

  useEffect(() => {
    mountedRef.current = true;
    flush().catch(() => undefined);

    const retry = () => flush().catch(() => undefined);
    const pageHide = () => {
      const snapshot = pendingRef.current ?? recordRef.current;
      localStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot));
      if (
        pendingRef.current ||
        snapshot.status === "draft" ||
        Number(snapshot.revision) > persistedRevisionRef.current
      ) {
        fetch(`/api/responses/${encodeURIComponent(snapshot.sessionId)}`, {
          method: "PUT",
          keepalive: true,
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${snapshot.editToken}`,
          },
          body: JSON.stringify({
            revision: snapshot.revision,
            currentStep: snapshot.currentStep,
            status: snapshot.status,
            answers: snapshot.answers,
            answerUpdatedAt: snapshot.answerUpdatedAt,
            startedAt: snapshot.startedAt,
            schemaVersion: snapshot.schemaVersion,
            taskCodes: snapshot.taskCodes,
          }),
        }).catch(() => undefined);
      }
    };
    const visibility = () => {
      if (document.visibilityState === "hidden") pageHide();
    };
    const storageChanged = (event) => {
      if (event.key !== STORAGE_KEY || !event.newValue) return;
      try {
        const incoming = JSON.parse(event.newValue);
        const current = recordRef.current;
        if (
          incoming.sessionId === current.sessionId &&
          Number(incoming.revision) > Number(current.revision)
        ) {
          recordRef.current = incoming;
          setRecord(incoming);
        }
      } catch {
        // Ignore malformed state from unrelated scripts or old versions.
      }
    };

    window.addEventListener("online", retry);
    window.addEventListener("pagehide", pageHide);
    window.addEventListener("storage", storageChanged);
    document.addEventListener("visibilitychange", visibility);
    return () => {
      mountedRef.current = false;
      clearTimeout(timerRef.current);
      clearTimeout(retryRef.current);
      window.removeEventListener("online", retry);
      window.removeEventListener("pagehide", pageHide);
      window.removeEventListener("storage", storageChanged);
      document.removeEventListener("visibilitychange", visibility);
    };
  }, [flush]);

  return {
    record,
    saveState,
    saveMessage,
    updateAnswer,
    moveToStep,
    complete,
    startNew,
    flush,
  };
}

function Question({ id, number, title, hint, children, error, className = "" }) {
  return (
    <fieldset
      className={`question ${className}${error ? " question--invalid" : ""}`}
      data-question={id}
    >
      <legend>
        {number && <span className="question-number">{number}</span>}
        <span>{title}</span>
      </legend>
      {hint && <p className="question-hint">{hint}</p>}
      {children}
      {error && <p className="field-error" role="alert">{error}</p>}
    </fieldset>
  );
}

function ChoiceList({ name, value, onChange, options, columns = 1 }) {
  return (
    <div className={`choice-list choice-list--${columns}`}>
      {options.map(([optionValue, label, description]) => (
        <label className={`choice-card${value === optionValue ? " choice-card--selected" : ""}`} key={optionValue}>
          <input
            type="radio"
            name={name}
            value={optionValue}
            checked={value === optionValue}
            onChange={() => onChange(optionValue)}
            aria-label={label}
          />
          <span className="radio-mark" aria-hidden="true" />
          <span>
            <strong>{label}</strong>
            {description && <small>{description}</small>}
          </span>
        </label>
      ))}
    </div>
  );
}

function MultiChoiceList({ name, value, onChange, options, columns = 1 }) {
  const selected = Array.isArray(value) ? value : value ? [value] : [];
  const toggle = (optionValue) => {
    if (optionValue === "none") return onChange(selected.includes("none") ? [] : ["none"]);
    const withoutNone = selected.filter((item) => item !== "none");
    onChange(withoutNone.includes(optionValue)
      ? withoutNone.filter((item) => item !== optionValue)
      : [...withoutNone, optionValue]);
  };
  return (
    <div className={`choice-list choice-list--${columns}`}>
      {options.map(([optionValue, label]) => (
        <label className={`choice-card${selected.includes(optionValue) ? " choice-card--selected" : ""}`} key={optionValue}>
          <input type="checkbox" name={name} value={optionValue} checked={selected.includes(optionValue)} onChange={() => toggle(optionValue)} />
          <span className="checkbox-mark" aria-hidden="true">✓</span>
          <span><strong>{label}</strong></span>
        </label>
      ))}
    </div>
  );
}

function LikertQuestion({ id, number, title, value, onChange, error, extraOption }) {
  const options = extraOption ? [...LIKERT, extraOption] : LIKERT;
  return (
    <Question id={id} number={number} title={title} error={error}>
      <div className="likert" role="radiogroup" aria-label={title}>
        {options.map(([optionValue, label]) => (
          <label
            className={`likert-option${value === optionValue ? " likert-option--selected" : ""}`}
            key={optionValue}
          >
            <input
              type="radio"
              name={id}
              value={optionValue}
              checked={value === optionValue}
              onChange={() => onChange(optionValue)}
              aria-label={`${optionValue}: ${label}`}
            />
            {typeof optionValue === "number" ? (
              <strong>{optionValue}</strong>
            ) : (
              <span className="radio-mark" aria-hidden="true" />
            )}
            <span>{label}</span>
          </label>
        ))}
      </div>
    </Question>
  );
}

function TaskCard({ label, title, steps, prompt, selectionHint }) {
  return (
    <div className="task-card">
      <div className="task-label"><span aria-hidden="true">◆</span>{label}</div>
      <h2>{title}</h2>
      {selectionHint && (
        <div className="selection-hint">
          <strong>So wählen Sie ein Objekt aus</strong>
          <p>{selectionHint}</p>
        </div>
      )}
      <ol>
        {steps.map((step) => <li key={step}>{step}</li>)}
      </ol>
      <div className="prompt-block">
        <span>Möglicher Fragevorschlag</span>
        <blockquote>{prompt}</blockquote>
        <p>Sie können die Frage gerne mit eigenen Worten formulieren.</p>
      </div>
      <p className="return-note">Warten Sie die Antwort ab und beantworten Sie danach die Fragen auf dieser Seite.</p>
    </div>
  );
}

function MatrixQuestion({ answers, onAnswer, errors }) {
  return (
    <section className="matrix-question" aria-labelledby="matrix-heading">
      <div className="section-heading">
        <span className="question-number">12</span>
        <div>
          <h2 id="matrix-heading">Aussagen zur gesamten Interaktion</h2>
          <p>Bewerten Sie jede Aussage von 1 „stimme überhaupt nicht zu“ bis 5 „stimme voll zu“.</p>
        </div>
      </div>
      <div className="matrix-scale-labels" aria-hidden="true">
        <span>stimme überhaupt nicht zu</span>
        <span>stimme voll zu</span>
      </div>
      <div className="matrix-rows">
        {Q8_ITEMS.map(([id, label], index) => (
          <fieldset
            className={`matrix-row${errors[id] ? " matrix-row--invalid" : ""}`}
            data-question={id}
            key={id}
          >
            <legend><span>{String.fromCharCode(97 + index)})</span>{label}</legend>
            <div className="matrix-options">
              {LIKERT.map(([number]) => (
                <label className={answers[id] === number ? "selected" : ""} key={number}>
                  <input
                    type="radio"
                    name={id}
                    value={number}
                  checked={answers[id] === number}
                  onChange={() => onAnswer(id, number)}
                  aria-label={`${number}: ${LIKERT[number - 1][1]}`}
                  />
                  <span>{number}</span>
                </label>
              ))}
            </div>
            {errors[id] && <p className="field-error" role="alert">{errors[id]}</p>}
          </fieldset>
        ))}
      </div>
    </section>
  );
}

function Progress({ step }) {
  const labels = ["Start", "Objekt", "Weiterleitung", "Bewertung", "Geschenk"];
  return (
    <nav className="progress" aria-label="Fortschritt im Fragebogen">
      <div className="progress-topline">
        <span>Schritt {step} von 5</span>
        <strong>{Math.round((step / 5) * 100)} %</strong>
      </div>
      <ol>
        {labels.map((label, index) => {
          const number = index + 1;
          return (
            <li
              className={`${number === step ? "active" : ""}${number < step ? " done" : ""}`}
              aria-current={number === step ? "step" : undefined}
              key={label}
            >
              <span>{number < step ? "✓" : number === 5 ? "🎁" : number}</span>
              <small>{label}</small>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

function validateStep(step, answers) {
  const errors = {};
  for (const field of STEP_FIELDS[step]) {
    if (answers[field] === undefined || answers[field] === null || answers[field] === "" ||
        (Array.isArray(answers[field]) && answers[field].length === 0)) {
      errors[field] = "Bitte beantworten Sie diese Frage.";
    }
  }
  if (step === 1 && answers.q1_device === "other" && !answers.q1_device_other?.trim()) {
    errors.q1_device_other = "Bitte geben Sie das verwendete Gerät an.";
  }
  return errors;
}

function findAllErrors(answers) {
  return Object.assign({}, ...[1, 2, 3, 4].map((step) => validateStep(step, answers)));
}

function focusFirstError(errors) {
  const first = Object.keys(errors)[0];
  if (!first) return;
  requestAnimationFrame(() => {
    const container = document.querySelector(`[data-question="${first}"]`);
    container?.scrollIntoView({ behavior: "smooth", block: "center" });
    container?.querySelector("input, textarea, button")?.focus({ preventScroll: true });
  });
}

function SaveIndicator({ state, message }) {
  return (
    <div className={`save-indicator save-indicator--${state}`} role="status" aria-live="polite">
      <span aria-hidden="true" />
      {message}
    </div>
  );
}

function Completion({ record, saveState, saveMessage, onNew }) {
  const canStartNew = saveState === "saved";
  const [identifier, setIdentifier] = useState("");
  const [eligibilityToken, setEligibilityToken] = useState("");
  const [raffleState, setRaffleState] = useState("loading");
  const [raffleMessage, setRaffleMessage] = useState("");

  useEffect(() => {
    if (saveState !== "saved") return;
    let active = true;
    fetch("/api/raffle-eligibility", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${record.editToken}` },
      body: JSON.stringify({ sessionId: record.sessionId }),
    }).then(async (response) => {
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || "Die Verlosung konnte nicht freigeschaltet werden.");
      if (active) { setEligibilityToken(payload.eligibilityToken); setRaffleState("ready"); }
    }).catch((error) => {
      if (active) { setRaffleState("error"); setRaffleMessage(error.message); }
    });
    return () => { active = false; };
  }, [record.editToken, record.sessionId, saveState]);

  const enterRaffle = async (event) => {
    event.preventDefault();
    setRaffleState("submitting");
    setRaffleMessage("");
    try {
      const response = await fetch("/api/raffle-entry", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ eligibilityToken, studyIdentifier: identifier }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || "Die Eintragung ist fehlgeschlagen.");
      setRaffleState("submitted");
    } catch (error) {
      setRaffleState("ready");
      setRaffleMessage(error.message);
    }
  };
  return (
    <div className="completion">
      <div className="completion-mark" aria-hidden="true">🎁</div>
      <span className="eyebrow">Teilnahme abgeschlossen</span>
      <h1>Vielen Dank für Ihre Unterstützung.</h1>
      <p>Optional können Sie jetzt an der Gutscheinverlosung teilnehmen.</p>
      <SaveIndicator state={saveState} message={saveMessage} />
      {saveState === "offline" && (
        <p className="completion-warning">
          Die Antworten sind in diesem Browser gesichert und werden automatisch übertragen, sobald die Verbindung wieder verfügbar ist.
        </p>
      )}
      {raffleState === "submitted" ? (
        <div className="raffle-success" role="status">
          <strong>Ihre Studierendenkennung wurde für die Verlosung gespeichert.</strong>
          <span>Sie ist technisch getrennt von Ihren Fragebogenantworten und kann diesen nicht zugeordnet werden.</span>
        </div>
      ) : (
        <form className="raffle-form" onSubmit={enterRaffle}>
          <label htmlFor="raffle-identifier">Studierendenkennung für die Verlosung <small>(freiwillig)</small></label>
          <p><strong>Kurzer Datenschutzhinweis (DSGVO):</strong> Die Angabe ist freiwillig und wird ausschließlich zur Durchführung der Gutscheinverlosung verarbeitet. Sie wird getrennt von Fragebogenantworten, Teilnahme-ID und Zeitstempeln gespeichert und nach Abschluss der Verlosung gelöscht. Eine Nichtteilnahme hat keine Nachteile.</p>
          <input id="raffle-identifier" value={identifier} onChange={(event) => setIdentifier(event.target.value)} minLength={3} maxLength={120} required disabled={raffleState !== "ready"} autoComplete="off" />
          {raffleMessage && <span className="field-error" role="alert">{raffleMessage}</span>}
          <button className="button button--primary" type="submit" disabled={raffleState !== "ready" || identifier.trim().length < 3}>
            {raffleState === "submitting" ? "Wird eingetragen …" : "An Verlosung teilnehmen"}
          </button>
        </form>
      )}
      <button
        className="button button--secondary"
        type="button"
        onClick={onNew}
        disabled={!canStartNew}
        title={canStartNew ? undefined : "Warten Sie, bis diese Teilnahme übertragen wurde."}
      >
        Neue Teilnahme starten
      </button>
    </div>
  );
}

function Questionnaire() {
  const {
    record,
    saveState,
    saveMessage,
    updateAnswer,
    moveToStep,
    complete,
    startNew,
    flush,
  } = useSurveySession();
  const [errors, setErrors] = useState({});
  const [expanded, setExpanded] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const topRef = useRef(null);
  const questionnaireRef = useRef(null);
  const answers = record.answers;
  const step = Math.min(4, Math.max(1, record.currentStep || 1));

  useEffect(() => {
    if (!expanded) return undefined;
    const close = (event) => {
      if (event.key === "Escape") setExpanded(false);
    };
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, [expanded]);

  const answer = useCallback((key, value, delay = 80) => {
    updateAnswer(key, value, delay);
    setErrors((current) => {
      if (!current[key] && !(key === "q1_device" && current.q1_device_other)) return current;
      const next = { ...current };
      delete next[key];
      if (key === "q1_device" && value !== "other") delete next.q1_device_other;
      return next;
    });
  }, [updateAnswer]);

  const goForward = async () => {
    const nextErrors = validateStep(step, answers);
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length) {
      focusFirstError(nextErrors);
      return;
    }
    moveToStep(step + 1);
    flush().catch(() => undefined);
    questionnaireRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const goBack = () => {
    setErrors({});
    moveToStep(Math.max(1, step - 1));
    flush().catch(() => undefined);
    questionnaireRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const submit = async () => {
    const allErrors = findAllErrors(answers);
    if (Object.keys(allErrors).length) {
      const firstField = Object.keys(allErrors)[0];
      const missingStep = Object.entries(STEP_FIELDS).find(([, fields]) => fields.includes(firstField))?.[0];
      if (missingStep && Number(missingStep) !== step) moveToStep(Number(missingStep));
      setErrors(allErrors);
      focusFirstError(allErrors);
      return;
    }
    setSubmitting(true);
    await complete();
    setSubmitting(false);
    questionnaireRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const renderStep = () => {
    if (step === 1) {
      return (
        <>
          <div className="page-heading">
            <span className="eyebrow">Kurze Evaluation</span>
            <h1>Erkunden Sie den virtuellen Messestand.</h1>
            <p>
              Der Messestand ist direkt neben beziehungsweise oberhalb dieses Fragebogens eingebettet. Bearbeiten Sie die Aufgaben in der 3D-Ansicht und beantworten Sie anschließend die zugehörigen Fragen. Die Ansicht bleibt beim Wechsel zwischen den Schritten geöffnet.
            </p>
          </div>

          <aside className="research-teaser" aria-labelledby="research-teaser-title">
            <span className="research-teaser-label">Forschungshintergrund</span>
            <h2 id="research-teaser-title">Von der Textbeschreibung zum interaktiven 3D-Raum</h2>
            <p>
              Hinter diesem Prototyp steht ein Metamodell, das die grundlegende Struktur des virtuellen Raums und seine Interaktionslogik vorgibt. Mit dieser Studie möchten wir untersuchen, wie gut dieses zugrunde liegende Modell in der praktischen Nutzung funktioniert.
            </p>
            <p>
              Sämtliche gezeigten Inhalte und 3D-Elemente wurden vollständig mithilfe generativer KI erstellt. Langfristiges Ziel der Forschung ist es, interaktive 3D-Räume künftig direkt aus natürlichsprachlichen Textbeschreibungen generieren zu können.
            </p>
          </aside>

          <div className="intro-card">
            <div className="time-chip"><span aria-hidden="true">◷</span> insgesamt etwa 5–10 Minuten</div>
            <h2>Worum geht es?</h2>
            <p>
              Im virtuellen Raum finden Sie unter anderem Empfang, Käseauslagen, Produktions- und Energiestationen, digitale Informationsstände, einen Karrierebereich und eine Lounge. Mehrere virtuelle Agenten besitzen unterschiedliche Aufgaben und Wissensbereiche.
            </p>
            <p>
              Wir untersuchen, wie verständlich und hilfreich die Interaktion mit Objekten und mehreren Agenten ist. Bei Ihren Bewertungen gibt es keine richtigen oder falschen Antworten.
            </p>
            <ul className="check-list">
              <li>Nutzen Sie möglichst einen Desktop-PC oder Laptop mit Maus und Tastatur.</li>
              <li>Ein VR-Headset ist nicht erforderlich.</li>
              <li>Ihre Antworten werden automatisch unter einer anonymen Teilnahme-ID gespeichert.</li>
            </ul>
          </div>

          <Question
            id="profile_age_group"
            number="1"
            title="Welcher Altersgruppe gehören Sie an?"
            error={errors.profile_age_group}
          >
            <ChoiceList
              name="profile_age_group"
              value={answers.profile_age_group}
              onChange={(value) => answer("profile_age_group", value)}
              options={[
                ["18_24", "18–24"], ["25_34", "25–34"], ["35_44", "35–44"],
                ["45_54", "45–54"], ["55_64", "55–64"], ["65_plus", "65 oder älter"],
                ["no_answer", "Keine Angabe"],
              ]}
              columns={2}
            />
          </Question>

          <Question
            id="profile_activity_field"
            number="2"
            title="Welchem Tätigkeits- oder Studienbereich ordnen Sie sich am ehesten zu?"
            error={errors.profile_activity_field}
          >
            <ChoiceList
              name="profile_activity_field"
              value={answers.profile_activity_field}
              onChange={(value) => answer("profile_activity_field", value)}
              options={[
                ["computer_science", "Informatik oder Softwareentwicklung"],
                ["design_hci", "Design, Medien, UX oder Human-Computer Interaction"],
                ["engineering", "Technik oder Ingenieurwesen"],
                ["business", "Wirtschaft, Verwaltung, Marketing oder Vertrieb"],
                ["education_research", "Bildung oder Forschung"],
                ["food_production", "Lebensmittelwirtschaft oder Produktion"],
                ["other_field", "Anderer Bereich"],
                ["no_answer", "Keine Angabe"],
              ]}
              columns={1}
            />
          </Question>

          <Question
            id="profile_ai_frequency"
            number="3"
            title="Wie häufig nutzen Sie dialogfähige KI-Systeme wie ChatGPT, Copilot, Gemini oder vergleichbare Anwendungen?"
            error={errors.profile_ai_frequency}
          >
            <ChoiceList
              name="profile_ai_frequency"
              value={answers.profile_ai_frequency}
              onChange={(value) => answer("profile_ai_frequency", value)}
              options={[
                ["never", "Nie"],
                ["less_than_monthly", "Seltener als einmal pro Monat"],
                ["monthly", "Ungefähr monatlich"],
                ["weekly", "Ungefähr wöchentlich"],
                ["daily", "Täglich oder fast täglich"],
              ]}
              columns={1}
            />
          </Question>

          <Question
            id="q1_device"
            number="4"
            title="Mit welchem Gerät nutzen Sie den virtuellen Messestand?"
            error={errors.q1_device}
          >
            <ChoiceList
              name="q1_device"
              value={answers.q1_device}
              onChange={(value) => answer("q1_device", value)}
              options={[
                ["desktop_laptop", "Desktop-PC oder Laptop", "im normalen Browser"],
                ["vr_headset", "VR-Headset"],
                ["tablet_smartphone", "Tablet oder Smartphone"],
                ["other", "Anderes Gerät"],
              ]}
              columns={2}
            />
            {answers.q1_device === "other" && (
              <label
                className={`text-field${errors.q1_device_other ? " text-field--invalid" : ""}`}
                data-question="q1_device_other"
              >
                <span>Welches Gerät verwenden Sie?</span>
                <input
                  type="text"
                  value={answers.q1_device_other ?? ""}
                  onChange={(event) => answer("q1_device_other", event.target.value, 350)}
                  maxLength={120}
                  autoComplete="off"
                />
                {errors.q1_device_other && <small className="field-error" role="alert">{errors.q1_device_other}</small>}
              </label>
            )}
          </Question>

          <Question
            id="q2_experience"
            number="5"
            title="Wie vertraut sind Sie mit dreidimensionalen Anwendungen, Videospielen oder Virtual Reality?"
            error={errors.q2_experience}
          >
            <ChoiceList
              name="q2_experience"
              value={answers.q2_experience}
              onChange={(value) => answer("q2_experience", value)}
              options={[
                [1, "Gar nicht vertraut"],
                [2, "Wenig vertraut"],
                [3, "Mäßig vertraut"],
                [4, "Sehr vertraut"],
              ]}
              columns={2}
            />
          </Question>
        </>
      );
    }

    if (step === 2) {
      return (
        <>
          <div className="page-heading">
            <span className="eyebrow">Aufgabe 1</span>
            <h1>Frage zu einem Objekt</h1>
            <p>Führen Sie die Aufgabe in der 3D-Ansicht aus. Die Ansicht läuft währenddessen weiter.</p>
          </div>
          <TaskCard
            label="Objektaufgabe"
            title="Wählen Sie ein Ausstellungsobjekt aus"
            selectionHint="Richten Sie in der 3D-Ansicht den Blick auf das gewünschte Objekt. Drücken Sie die Taste E oder betätigen Sie den eingeblendeten „Ansehen“-Button. Eine sichtbare Hervorhebung zeigt Ihnen, dass das Objekt ausgewählt ist."
            steps={[
              "Gehen Sie zum Bereich mit den Käseprodukten.",
              "Wählen Sie dort eine gut sichtbare Käsetheke oder einen Produktsockel aus.",
              "Prüfen Sie kurz, ob das Objekt hervorgehoben oder als ausgewählt angezeigt wird.",
              "Sprechen Sie mit dem Cheese Expert, dem Agenten für Käseprodukte.",
            ]}
            prompt="Was erfahre ich an diesem Ausstellungsobjekt über die hier präsentierten Käseprodukte?"
          />
          <LikertQuestion
            id="q3_object_selection_clarity"
            number="6"
            title="Es war für mich klar erkennbar, welches Objekt ich ausgewählt hatte."
            value={answers.q3_object_selection_clarity}
            onChange={(value) => answer("q3_object_selection_clarity", value)}
            error={errors.q3_object_selection_clarity}
          />
          <LikertQuestion
            id="q4_object_answer_fit"
            number="7"
            title="Die Antwort des Agenten bezog sich nachvollziehbar auf das ausgewählte Objekt und auf meine Frage."
            value={answers.q4_object_answer_fit}
            onChange={(value) => answer("q4_object_answer_fit", value)}
            error={errors.q4_object_answer_fit}
          />
        </>
      );
    }

    if (step === 3) {
      return (
        <>
          <div className="page-heading">
            <span className="eyebrow">Aufgabe 2</span>
            <h1>Weiterleitung zwischen Agenten</h1>
            <p>Achten Sie darauf, ob ein anderer Agent beteiligt wird und wer Ihre Frage beantwortet.</p>
          </div>
          <TaskCard
            label="Weiterleitungsaufgabe"
            title="Stellen Sie eine fachbezogene Frage am Empfang"
            steps={[
              "Aktivieren Sie den Welcome Host im Empfangsbereich.",
              "Für diese Aufgabe müssen Sie kein bestimmtes Objekt auswählen.",
              "Warten Sie, bis die Interaktion vollständig abgeschlossen ist.",
            ]}
            prompt="Welche Käseprodukte kann ich hier probieren, und wer kann mir mehr darüber erklären?"
          />
          <Question
            id="q5_handoff_observed"
            number="8"
            title="Wurde Ihre Frage an einen anderen Agenten weitergeleitet?"
            error={errors.q5_handoff_observed}
          >
            <ChoiceList
              name="q5_handoff_observed"
              value={answers.q5_handoff_observed}
              onChange={(value) => answer("q5_handoff_observed", value)}
              options={[["yes", "Ja"], ["no", "Nein"], ["unsure", "Ich bin mir nicht sicher"]]}
              columns={3}
            />
          </Question>
          <LikertQuestion
            id="q6_handoff_understandability"
            number="9"
            title="Die Weiterleitung an einen anderen Agenten war für mich verständlich."
            value={answers.q6_handoff_understandability}
            onChange={(value) => answer("q6_handoff_understandability", value)}
            error={errors.q6_handoff_understandability}
            extraOption={["not_experienced", "keine Weiterleitung erlebt"]}
          />
          <LikertQuestion
            id="q7_final_agent_clarity"
            number="10"
            title="Nach der Weiterleitung war für mich klar, welcher Agent meine Frage beantwortete."
            value={answers.q7_final_agent_clarity}
            onChange={(value) => answer("q7_final_agent_clarity", value)}
            error={errors.q7_final_agent_clarity}
            extraOption={["not_experienced", "keine Weiterleitung erlebt"]}
          />
        </>
      );
    }

    return (
      <>
        <div className="page-heading">
          <span className="eyebrow">Abschluss</span>
          <h1>Bewerten Sie Ihre gesamte Erfahrung.</h1>
          <p>Denken Sie dabei an beide Aufgaben und an Ihre Orientierung im virtuellen Messestand.</p>
        </div>
        <LikertQuestion
          id="q13_multi_agent_help"
          number="11"
          title="Die Aufteilung auf mehrere Agenten mit unterschiedlichen Aufgaben half mir, die passenden Informationen zu erhalten."
          value={answers.q13_multi_agent_help}
          onChange={(value) => answer("q13_multi_agent_help", value)}
          error={errors.q13_multi_agent_help}
        />
        <MatrixQuestion answers={answers} onAnswer={answer} errors={errors} />
        <LikertQuestion
          id="q9_error_explanation"
          number="13"
          title="Wenn eine Frage nicht beantwortet oder eine Aktion nicht ausgeführt werden konnte, erklärte das System den Grund verständlich."
          value={answers.q9_error_explanation}
          onChange={(value) => answer("q9_error_explanation", value)}
          error={errors.q9_error_explanation}
          extraOption={["not_experienced", "keine solche Situation erlebt"]}
        />
        <Question
          id="q10_agent_selection_model"
          number="14"
          title="Welche Aussage beschreibt Ihrer Einschätzung nach am besten, wie das System bestimmt, welcher Agent eine Frage beantwortet?"
          error={errors.q10_agent_selection_model}
        >
          <ChoiceList
            name="q10_agent_selection_model"
            value={answers.q10_agent_selection_model}
            onChange={(value) => answer("q10_agent_selection_model", value)}
            options={[
              ["object_and_topic", "Das ausgewählte Objekt und das Thema der Frage bestimmen, welcher Agent zuständig ist."],
              ["nearest_agent", "Der Agent, der der nutzenden Person räumlich am nächsten steht, beantwortet die Frage."],
              ["first_contacted", "Immer der zuerst angesprochene Agent beantwortet die Frage."],
              ["random", "Der antwortende Agent wird zufällig ausgewählt."],
              ["unclear", "Ich konnte nicht erkennen, wie der zuständige Agent ausgewählt wurde."],
            ]}
          />
        </Question>
        <Question
          id="q11_overall_score"
          number="15"
          title="Wie gut funktionierte die Interaktion mit den Objekten und Agenten insgesamt?"
          hint="0 bedeutet „überhaupt nicht gut“, 10 bedeutet „ausgezeichnet“."
          error={errors.q11_overall_score}
        >
          <div className="score-scale" role="radiogroup" aria-label="Gesamturteil von 0 bis 10">
            {Array.from({ length: 11 }, (_, value) => (
              <label className={answers.q11_overall_score === value ? "selected" : ""} key={value}>
                <input
                  type="radio"
                  name="q11_overall_score"
                  value={value}
                  checked={answers.q11_overall_score === value}
                  onChange={() => answer("q11_overall_score", value)}
                  aria-label={`${value} von 10`}
                />
                <span>{value}</span>
              </label>
            ))}
          </div>
          <div className="score-anchors"><span>überhaupt nicht gut</span><span>ausgezeichnet</span></div>
        </Question>
        <Question
          id="q14_best_use_case"
          number="16"
          title="Für welchen Anwendungsbereich wäre eine solche virtuelle Umgebung aus Ihrer Sicht am sinnvollsten?"
          hint="Mehrfachauswahl möglich"
          error={errors.q14_best_use_case}
        >
          <MultiChoiceList
            name="q14_best_use_case"
            value={answers.q14_best_use_case}
            onChange={(value) => answer("q14_best_use_case", value)}
            options={[
              ["trade_fair", "Virtueller Messestand oder Unternehmenspräsentation"],
              ["product_information", "Produktinformation oder Produktberatung"],
              ["museum", "Museum oder Ausstellung"],
              ["learning", "Lernen, Schulung oder Weiterbildung"],
              ["recruiting", "Karriereinformation oder Recruiting"],
              ["customer_service", "Kundenservice"],
              ["none", "Für keinen dieser Bereiche"],
              ["other_use_case", "Anderer Bereich"],
            ]}
            columns={1}
          />
        </Question>
        <Question
          id="q12_improvement"
          number="17"
          title="Was sollte an der Interaktion am dringendsten verbessert werden?"
          hint="Optional"
        >
          <label className="textarea-field">
            <span className="sr-only">Ihre wichtigste Verbesserung</span>
            <textarea
              value={answers.q12_improvement ?? ""}
              onChange={(event) => answer("q12_improvement", event.target.value, 350)}
              maxLength={2000}
              rows={5}
              placeholder="Ihre Beobachtung oder Ihr Verbesserungsvorschlag …"
            />
            <small>{(answers.q12_improvement ?? "").length} / 2.000 Zeichen</small>
          </label>
        </Question>
      </>
    );
  };

  return (
    <div className="study-app" ref={topRef}>
      <header className="site-header">
        <a className="brand" href="/" aria-label="Käsesteinpilz Interaktionsstudie">
          <span className="brand-mark" aria-hidden="true">KS</span>
          <span><strong>Käsesteinpilz</strong><small>Interaktionsstudie</small></span>
        </a>
        <div className="header-meta">
          <span className="session-label">ID {record.sessionId.slice(0, 8)}</span>
          <SaveIndicator state={saveState} message={saveMessage} />
        </div>
      </header>

      <main className="study-layout">
        <UnityLoader
          expanded={expanded}
          onToggleExpanded={() => setExpanded((value) => !value)}
        />
        <section className="questionnaire-panel" aria-label="Fragebogen" ref={questionnaireRef}>
          <Progress step={record.status === "completed" ? 5 : step} />
          {record.status === "completed" ? (
            <Completion
              record={record}
              saveState={saveState}
              saveMessage={saveMessage}
              onNew={startNew}
            />
          ) : (
            <>
              <div className="questionnaire-content">{renderStep()}</div>
              <div className="form-actions">
                {step > 1 ? (
                  <button className="button button--secondary" type="button" onClick={goBack}>
                    Zurück
                  </button>
                ) : <span />}
                {step < 4 ? (
                  <button className="button button--primary" type="button" onClick={goForward}>
                    Weiter <span aria-hidden="true">→</span>
                  </button>
                ) : (
                  <button
                    className="button button--primary"
                    type="button"
                    onClick={submit}
                    disabled={submitting}
                  >
                    {submitting ? "Wird abgeschlossen …" : "Antworten absenden"}
                  </button>
                )}
              </div>
            </>
          )}
          <footer className="panel-footer">
            <span>Anonyme Erhebung · Antworten werden automatisch gespeichert</span>
            <span className="panel-footer-links">
              <a href="https://www.hochschuljobboerse.de/en/impressum" target="_blank" rel="noreferrer">Impressum</a>
              <a href="/admin.html">Studienleitung</a>
            </span>
          </footer>
        </section>
      </main>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <Questionnaire />
  </React.StrictMode>,
);
