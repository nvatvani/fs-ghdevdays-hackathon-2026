const form = document.querySelector("#roast-form");
const ideaInput = document.querySelector("#idea");
const charCount = document.querySelector("#char-count");
const submitButton = document.querySelector("#submit-button");
const result = document.querySelector("#result");
const roastContent = document.querySelector("#roast-content");
const errorMessage = document.querySelector("#error-message");
const copyButton = document.querySelector("#copy-button");
const modelStatus = document.querySelector("#model-status");
const modelStatusLabel = document.querySelector("#model-status-label");
const settingsDrawer = document.querySelector("#settings-drawer");
const settingsTab = document.querySelector("#settings-tab");
const settingsClose = document.querySelector("#settings-close");
const settingsForm = document.querySelector("#settings-form");
const resetSettings = document.querySelector("#reset-settings");
const settingsStatus = document.querySelector("#settings-status");
const availableModels = document.querySelector("#available-models");
const modelOptions = document.querySelector("#model-options");
const footerModelName = document.querySelector("#footer-model-name");
const settingsFields = {
  model_url: document.querySelector("#model-url"),
  model_name: document.querySelector("#model-name"),
  model_timeout: document.querySelector("#model-timeout"),
  api_key: document.querySelector("#api-key"),
};
let defaults = null;
let settings = null;

function readSettings() {
  return {
    model_url: settingsFields.model_url.value.trim(),
    model_name: settingsFields.model_name.value.trim(),
    model_timeout: Number(settingsFields.model_timeout.value),
    api_key: settingsFields.api_key.value,
  };
}

function populateSettings(values) {
  Object.entries(values).forEach(([key, value]) => {
    settingsFields[key].value = value;
  });
  footerModelName.textContent = values.model_name || "UNKNOWN MODEL";
}

function loadSettings() {
  const saved = JSON.parse(localStorage.getItem("roast-my-pitch-settings") || "null");
  settings = saved || { ...defaults };
  populateSettings(settings);
}

function openSettings() {
  settingsDrawer.classList.add("is-open");
  settingsTab.setAttribute("aria-expanded", "true");
  settingsFields.model_url.focus();
}

function closeSettings() {
  settingsDrawer.classList.remove("is-open");
  settingsTab.setAttribute("aria-expanded", "false");
}

async function initializeSettings() {
  try {
    const response = await fetch("/api/config", { cache: "no-store" });
    defaults = await response.json();
    loadSettings();
  } catch {
    settingsStatus.textContent = "Could not load the server defaults.";
  }
}

async function checkModelStatus() {
  if (!settings) return;
  try {
    const response = await fetch("/api/model-status", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(settings),
      cache: "no-store",
    });
    const payload = await response.json();
    const online = response.ok && payload.online;
    modelStatus.classList.toggle("is-online", online);
    modelStatus.classList.toggle("is-offline", !online);
    modelStatusLabel.textContent = online
      ? "LOCAL MODEL / ONLINE"
      : "LOCAL MODEL / OFFLINE";
  } catch {
    modelStatus.classList.remove("is-online");
    modelStatus.classList.add("is-offline");
    modelStatusLabel.textContent = "LOCAL MODEL / OFFLINE";
  }
}

async function loadAvailableModels() {
  availableModels.textContent = "Loading available models...";
  try {
    const response = await fetch("/api/models", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(settings),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "Could not load models.");
    modelOptions.replaceChildren(
      ...payload.models.map((model) => {
        const option = document.createElement("option");
        option.value = model;
        return option;
      }),
    );
    availableModels.textContent = payload.models.length
      ? `Available models: ${payload.models.join(", ")}`
      : "No models were returned by this endpoint.";
  } catch (error) {
    modelOptions.replaceChildren();
    availableModels.textContent = error.message;
  }
}

initializeSettings().then(() => {
  checkModelStatus();
  loadAvailableModels();
  setInterval(checkModelStatus, 3000);
});

settingsTab.addEventListener("click", () => {
  settingsDrawer.classList.contains("is-open") ? closeSettings() : openSettings();
});
settingsClose.addEventListener("click", closeSettings);

settingsForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  settings = readSettings();
  localStorage.setItem("roast-my-pitch-settings", JSON.stringify(settings));
  populateSettings(settings);
  settingsStatus.textContent = "Saved. Checking endpoint and loading models...";
  checkModelStatus();
  await loadAvailableModels();
  settingsStatus.textContent = "Settings saved.";
});

resetSettings.addEventListener("click", () => {
  settings = { ...defaults };
  populateSettings(settings);
  localStorage.removeItem("roast-my-pitch-settings");
  settingsStatus.textContent = "Defaults restored.";
  checkModelStatus();
  loadAvailableModels();
});

ideaInput.addEventListener("input", () => {
  charCount.textContent = `${ideaInput.value.length.toLocaleString()} / 8,000`;
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  result.hidden = true;
  errorMessage.hidden = true;
  submitButton.disabled = true;
  submitButton.classList.add("is-loading");

  try {
    const response = await fetch("/api/roast", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ idea: ideaInput.value, ...settings }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "The roast failed.");
    roastContent.textContent = payload.roast;
    result.hidden = false;
    result.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    errorMessage.textContent = error.message;
    errorMessage.hidden = false;
  } finally {
    submitButton.disabled = false;
    submitButton.classList.remove("is-loading");
  }
});

copyButton.addEventListener("click", async () => {
  await navigator.clipboard.writeText(roastContent.textContent);
  copyButton.textContent = "Copied";
  setTimeout(() => { copyButton.textContent = "Copy roast"; }, 1600);
});
