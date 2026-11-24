// ============================================================
// Loan Risk Predictor - Frontend Logic
// ============================================================

// Get HTML elements
const loanForm = document.getElementById("loanForm");

const predictButton = document.getElementById("predictButton");

const loading = document.getElementById("loading");

const resultCard = document.getElementById("resultCard");

const errorMessage = document.getElementById("errorMessage");

const riskClass = document.getElementById("riskClass");

const riskBadge = document.getElementById("riskBadge");

const probability = document.getElementById("probability");

const threshold = document.getElementById("threshold");

const resetButton = document.getElementById("resetButton");

// ============================================================
// Form Submission
// ============================================================

loanForm.addEventListener("submit", async function (event) {
  // Prevent normal page refresh
  event.preventDefault();

  // Hide previous messages/results
  resultCard.classList.add("hidden");
  errorMessage.classList.add("hidden");

  // Show loading state
  loading.classList.remove("hidden");

  predictButton.disabled = true;

  try {
    // ====================================================
    // Collect form data
    // ====================================================

    const formData = new FormData(loanForm);

    const applicant = {
      AMT_INCOME_TOTAL: Number(formData.get("AMT_INCOME_TOTAL")),

      AMT_CREDIT: Number(formData.get("AMT_CREDIT")),

      AMT_ANNUITY: Number(formData.get("AMT_ANNUITY")),

      AMT_GOODS_PRICE: Number(formData.get("AMT_GOODS_PRICE")),

      EXT_SOURCE_1: Number(formData.get("EXT_SOURCE_1")),

      EXT_SOURCE_2: Number(formData.get("EXT_SOURCE_2")),

      EXT_SOURCE_3: Number(formData.get("EXT_SOURCE_3")),

      AGE_YEARS: Number(formData.get("AGE_YEARS")),

      EMPLOYED_YEARS: Number(formData.get("EMPLOYED_YEARS")),

      NAME_CONTRACT_TYPE: formData.get("NAME_CONTRACT_TYPE"),

      NAME_EDUCATION_TYPE: formData.get("NAME_EDUCATION_TYPE"),

      NAME_INCOME_TYPE: formData.get("NAME_INCOME_TYPE"),

      OCCUPATION_TYPE: formData.get("OCCUPATION_TYPE"),

      NAME_FAMILY_STATUS: formData.get("NAME_FAMILY_STATUS"),

      FLAG_OWN_CAR: formData.get("FLAG_OWN_CAR"),

      DEF_30_CNT_SOCIAL_CIRCLE: Number(
        formData.get("DEF_30_CNT_SOCIAL_CIRCLE"),
      ),

      DEF_60_CNT_SOCIAL_CIRCLE: Number(
        formData.get("DEF_60_CNT_SOCIAL_CIRCLE"),
      ),

      REGION_RATING_CLIENT: Number(formData.get("REGION_RATING_CLIENT")),
    };

    // ====================================================
    // Send request to Flask API
    // ====================================================

    const response = await fetch("/predict", {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify(applicant),
    });

    // Convert response to JSON
    const data = await response.json();

    // ====================================================
    // Handle API errors
    // ====================================================

    if (!response.ok) {
      throw new Error(data.error || "Unable to process the prediction.");
    }

    // ====================================================
    // Display prediction
    // ====================================================

    const probabilityPercent = data.default_probability * 100;

    probability.textContent = probabilityPercent.toFixed(2);

    threshold.textContent = (data.threshold * 100).toFixed(0) + "%";

    riskClass.textContent = data.risk_class;

    // ====================================================
    // Risk badge
    // ====================================================

    if (data.prediction === 1) {
      riskBadge.textContent = "HIGHER RISK";

      riskBadge.style.background = "#fef2f2";

      riskBadge.style.color = "#dc2626";
    } else {
      riskBadge.textContent = "LOWER RISK";

      riskBadge.style.background = "#ecfdf3";

      riskBadge.style.color = "#15803d";
    }

    // Show result
    resultCard.classList.remove("hidden");

    // Scroll to result
    resultCard.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  } catch (error) {
    // ====================================================
    // Display error
    // ====================================================

    errorMessage.textContent = error.message;

    errorMessage.classList.remove("hidden");

    errorMessage.scrollIntoView({
      behavior: "smooth",
      block: "center",
    });
  } finally {
    // Hide loading
    loading.classList.add("hidden");

    // Re-enable button
    predictButton.disabled = false;
  }
});

// ============================================================
// Reset / New Prediction
// ============================================================

resetButton.addEventListener("click", function () {
  // Hide result
  resultCard.classList.add("hidden");

  // Hide errors
  errorMessage.classList.add("hidden");

  // Scroll back to form
  loanForm.scrollIntoView({
    behavior: "smooth",
    block: "start",
  });
});
