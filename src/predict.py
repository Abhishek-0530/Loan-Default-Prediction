import joblib
import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# 1. Load V2 Deployment Model
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR /
    "models" /
    "loan_default_deployment_v2.pkl"
)

model_bundle = joblib.load(MODEL_PATH)

model = model_bundle["model"]
threshold = model_bundle["threshold"]
deployment_features = model_bundle["features"]


# ============================================================
# 2. Validate Applicant Input
# ============================================================

def validate_applicant_data(data):

    errors = []

    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

    required_fields = [
        "AMT_INCOME_TOTAL",
        "AMT_CREDIT",
        "AMT_ANNUITY",
        "AMT_GOODS_PRICE",
        "EXT_SOURCE_1",
        "EXT_SOURCE_2",
        "EXT_SOURCE_3",
        "AGE_YEARS",
        "EMPLOYED_YEARS",
        "NAME_CONTRACT_TYPE",
        "NAME_EDUCATION_TYPE",
        "NAME_INCOME_TYPE",
        "OCCUPATION_TYPE",
        "NAME_FAMILY_STATUS",
        "FLAG_OWN_CAR",
        "DEF_30_CNT_SOCIAL_CIRCLE",
        "DEF_60_CNT_SOCIAL_CIRCLE",
        "REGION_RATING_CLIENT"
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in data
    ]

    if missing_fields:
        errors.append(
            f"Missing required fields: {missing_fields}"
        )

    # Stop here if required fields are missing
    if errors:
        return errors

    # --------------------------------------------------------
    # Numeric validation helper
    # --------------------------------------------------------

    def check_non_negative(field):

        try:
            value = float(data[field])

            if value < 0:
                errors.append(
                    f"{field} cannot be negative."
                )

        except (TypeError, ValueError):
            errors.append(
                f"{field} must be a valid number."
            )

    # --------------------------------------------------------
    # Financial fields
    # --------------------------------------------------------

    for field in [
        "AMT_INCOME_TOTAL",
        "AMT_CREDIT",
        "AMT_ANNUITY",
        "AMT_GOODS_PRICE"
    ]:
        check_non_negative(field)

    # --------------------------------------------------------
    # Age validation
    # --------------------------------------------------------

    try:
        age = float(data["AGE_YEARS"])

        if age < 18 or age > 100:
            errors.append(
                "AGE_YEARS must be between 18 and 100."
            )

    except (TypeError, ValueError):
        errors.append(
            "AGE_YEARS must be a valid number."
        )

    # --------------------------------------------------------
    # Employment years validation
    # --------------------------------------------------------

    try:
        employment_years = float(data["EMPLOYED_YEARS"])

        if employment_years < 0:
            errors.append(
                "EMPLOYED_YEARS cannot be negative."
            )

        elif employment_years > 70:
            errors.append(
                "EMPLOYED_YEARS must be 70 years or less."
            )

    except (TypeError, ValueError):
        errors.append(
            "EMPLOYED_YEARS must be a valid number."
        )

    # --------------------------------------------------------
    # External credit source validation
    # Expected range: 0 to 1
    # --------------------------------------------------------

    for field in [
        "EXT_SOURCE_1",
        "EXT_SOURCE_2",
        "EXT_SOURCE_3"
    ]:

        try:
            value = float(data[field])

            if value < 0 or value > 1:
                errors.append(
                    f"{field} must be between 0 and 1."
                )

        except (TypeError, ValueError):
            errors.append(
                f"{field} must be a valid number."
            )

    # --------------------------------------------------------
    # Social-circle default counts
    # --------------------------------------------------------

    for field in [
        "DEF_30_CNT_SOCIAL_CIRCLE",
        "DEF_60_CNT_SOCIAL_CIRCLE"
    ]:
        try:
            value = float(data[field])

            if value < 0:
                errors.append(
                    f"{field} cannot be negative."
                )

        except (TypeError, ValueError):
            errors.append(
                f"{field} must be a valid number."
            )

    # --------------------------------------------------------
    # Region rating
    # --------------------------------------------------------

    try:
        region_rating = int(data["REGION_RATING_CLIENT"])

        if region_rating not in [1, 2, 3]:
            errors.append(
                "REGION_RATING_CLIENT must be 1, 2, or 3."
            )

    except (TypeError, ValueError):
        errors.append(
            "REGION_RATING_CLIENT must be 1, 2, or 3."
        )

    # --------------------------------------------------------
    # Car ownership
    # --------------------------------------------------------

    if data["FLAG_OWN_CAR"] not in ["Y", "N"]:
        errors.append(
            "FLAG_OWN_CAR must be either 'Y' or 'N'."
        )

    return errors


# ============================================================
# 3. Prepare Applicant Data
# ============================================================

def prepare_applicant_data(applicant_data):

    data = applicant_data.copy()

    # --------------------------------------------------------
    # Convert Age → DAYS_BIRTH
    # --------------------------------------------------------

    if "AGE_YEARS" in data:
        data["DAYS_BIRTH"] = (
            -float(data.pop("AGE_YEARS")) * 365
        )

    # --------------------------------------------------------
    # Convert Employment Years → DAYS_EMPLOYED
    # --------------------------------------------------------

    if "EMPLOYED_YEARS" in data:

        employment_years = data.pop("EMPLOYED_YEARS")

        if employment_years is None:
            data["DAYS_EMPLOYED"] = np.nan
        else:
            data["DAYS_EMPLOYED"] = (
                -float(employment_years) * 365
            )

    # --------------------------------------------------------
    # Handle Home Credit special missing-value code
    # --------------------------------------------------------

    if "DAYS_EMPLOYED" in data:

        if data["DAYS_EMPLOYED"] == 365243:
            data["DAYS_EMPLOYED"] = np.nan

    # --------------------------------------------------------
    # Create DataFrame
    # --------------------------------------------------------

    input_data = pd.DataFrame([data])

    # --------------------------------------------------------
    # Check model features
    # --------------------------------------------------------

    missing_features = [
        feature
        for feature in deployment_features
        if feature not in input_data.columns
    ]

    if missing_features:
        raise ValueError(
            f"Missing required model features: {missing_features}"
        )

    # --------------------------------------------------------
    # Keep only deployment features
    # --------------------------------------------------------

    input_data = input_data[deployment_features]

    return input_data


# ============================================================
# 4. Prediction Function
# ============================================================

def predict_loan_risk(applicant_data):

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    validation_errors = validate_applicant_data(
        applicant_data
    )

    if validation_errors:

        raise ValueError(
            "Input validation failed: "
            + " | ".join(validation_errors)
        )

    # --------------------------------------------------------
    # Prepare data
    # --------------------------------------------------------

    input_data = prepare_applicant_data(
        applicant_data
    )

    # --------------------------------------------------------
    # Model probability
    # --------------------------------------------------------

    probability = model.predict_proba(
        input_data
    )[0, 1]

    # --------------------------------------------------------
    # Apply threshold
    # --------------------------------------------------------

    prediction = int(
        probability >= threshold
    )

    # --------------------------------------------------------
    # Risk classification
    # --------------------------------------------------------

    if prediction == 1:

        risk_class = (
            "Higher predicted default risk"
        )

    else:

        risk_class = (
            "Lower predicted default risk"
        )

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {
        "default_probability": round(
            float(probability),
            4
        ),

        "threshold": round(
            float(threshold),
            4
        ),

        "prediction": prediction,

        "risk_class": risk_class
    }