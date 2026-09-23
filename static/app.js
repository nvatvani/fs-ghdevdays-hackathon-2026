const form = document.querySelector("#roast-form");
const ideaInput = document.querySelector("#idea");
const charCount = document.querySelector("#char-count");
const submitButton = document.querySelector("#submit-button");
const result = document.querySelector("#result");
const roastContent = document.querySelector("#roast-content");
const errorMessage = document.querySelector("#error-message");
const copyButton = document.querySelector("#copy-button");

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
      body: JSON.stringify({ idea: ideaInput.value }),
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
