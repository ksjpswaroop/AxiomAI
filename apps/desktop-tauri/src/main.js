const invoke = window.__TAURI__?.tauri?.invoke;

function setOutput(id, value) {
  const el = document.getElementById(id);
  if (!el) return;
  if (typeof value === "string") {
    el.textContent = value;
    return;
  }
  el.textContent = JSON.stringify(value, null, 2);
}

async function proxy(method, url, body) {
  if (!invoke) {
    throw new Error("Tauri invoke API is unavailable");
  }
  return invoke("proxy_json", { method, url, body: body ?? null });
}

function apiBase() {
  return document.getElementById("apiUrl").value.trim().replace(/\/$/, "");
}

function parseActionJson() {
  const raw = document.getElementById("actionJson").value;
  return JSON.parse(raw);
}

function parseContextLines() {
  return document
    .getElementById("contextLines")
    .value.split("\n")
    .map((x) => x.trim())
    .filter(Boolean);
}

function parseFactLines() {
  return document
    .getElementById("webhookFacts")
    .value.split("\n")
    .map((x) => x.trim())
    .filter(Boolean);
}

document.getElementById("healthBtn").addEventListener("click", async () => {
  setOutput("healthOut", "Checking...");
  try {
    const out = await proxy("GET", `${apiBase()}/health`);
    setOutput("healthOut", out);
  } catch (err) {
    setOutput("healthOut", `Error: ${err}`);
  }
});

document.getElementById("governBtn").addEventListener("click", async () => {
  setOutput("governOut", "Validating...");
  try {
    const payload = {
      action: parseActionJson(),
      context: parseContextLines(),
      policy_id: document.getElementById("policyId").value,
    };
    const caseStudy = document.getElementById("caseStudy").value.trim();
    if (caseStudy) {
      payload.case_study = caseStudy;
    }
    const out = await proxy("POST", `${apiBase()}/governance/validate`, payload);
    setOutput("governOut", out);
  } catch (err) {
    setOutput("governOut", `Error: ${err}`);
  }
});

document.getElementById("webhookBtn").addEventListener("click", async () => {
  setOutput("webhookOut", "Sending...");
  try {
    const out = await proxy("POST", `${apiBase()}/connectors/webhook/facts`, {
      facts: parseFactLines(),
    });
    setOutput("webhookOut", out);
  } catch (err) {
    setOutput("webhookOut", `Error: ${err}`);
  }
});

document.getElementById("caseRunBtn").addEventListener("click", async () => {
  setOutput("caseOut", "Running...");
  try {
    const caseId = document.getElementById("caseStudyId").value;
    const scenario = document.getElementById("scenarioId").value || "default";
    const out = await proxy("POST", `${apiBase()}/case-studies/${caseId}/run`, {
      scenario,
    });
    setOutput("caseOut", out);
  } catch (err) {
    setOutput("caseOut", `Error: ${err}`);
  }
});
