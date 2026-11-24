import pandas as pd
import numpy as np
import joblib


# ==========================================
# 1. Load dataset
# ==========================================

df = pd.read_csv("data/raw/application_train.csv")


# ==========================================
# 2. Select same applicant
# ==========================================

applicant = df.drop(
    columns=["TARGET", "SK_ID_CURR"]
).iloc[0].to_dict()


# Convert NaN to None
applicant = {
    key: None if pd.isna(value) else value
    for key, value in applicant.items()
}


# ==========================================
# 3. Convert to DataFrame
# ==========================================

input_data = pd.DataFrame([applicant])


# ==========================================
# 4. SAME feature engineering as API
# ==========================================

input_data["DAYS_EMPLOYED"] = input_data["DAYS_EMPLOYED"].replace(
    365243,
    np.nan
)

input_data["CREDIT_INCOME_RATIO"] = (
    input_data["AMT_CREDIT"] /
    (input_data["AMT_INCOME_TOTAL"] + 1)
)

input_data["ANNUITY_INCOME_RATIO"] = (
    input_data["AMT_ANNUITY"] /
    (input_data["AMT_INCOME_TOTAL"] + 1)
)

input_data["CREDIT_GOODS_RATIO"] = (
    input_data["AMT_CREDIT"] /
    (input_data["AMT_GOODS_PRICE"] + 1)
)

input_data["AGE_YEARS"] = (
    -input_data["DAYS_BIRTH"] / 365
)

input_data["EMPLOYED_YEARS"] = (
    -input_data["DAYS_EMPLOYED"] / 365
)


# ==========================================
# 5. Load saved model
# ==========================================

bundle = joblib.load(
    "models/loan_default_model.pkl"
)

model = bundle["model"]
threshold = bundle["threshold"]


# ==========================================
# 6. Predict
# ==========================================

probability = model.predict_proba(
    input_data
)[0, 1]

prediction = int(
    probability >= threshold
)


# ==========================================
# 7. Display result
# ==========================================

print("=" * 50)

print("DIRECT SAVED MODEL TEST")

print("=" * 50)

print(
    "Probability:",
    round(float(probability), 4)
)

print(
    "Threshold:",
    threshold
)

print(
    "Prediction:",
    prediction
)

print("=" * 50)