import pandas as pd
import numpy as np
import joblib
import requests

# 1. Load the dataset
df = pd.read_csv("data/raw/application_train.csv")

# 2. Select the first applicant
applicant = df.drop(
    columns=["TARGET", "SK_ID_CURR"]
).iloc[0].to_dict()

# 3. Convert missing values to None for JSON
applicant = {
    key: None if pd.isna(value) else value
    for key, value in applicant.items()
}

# 4. Load the saved model
bundle = joblib.load("models/loan_default_model.pkl")
model = bundle["model"]
threshold = bundle["threshold"]

# 5. Apply the same feature engineering as the API
input_data = pd.DataFrame([applicant])

input_data["DAYS_EMPLOYED"] = input_data["DAYS_EMPLOYED"].replace(
    365243, np.nan
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

input_data["AGE_YEARS"] = -input_data["DAYS_BIRTH"] / 365

input_data["EMPLOYED_YEARS"] = (
    -input_data["DAYS_EMPLOYED"] / 365
)

# 6. Get direct model prediction
direct_probability = model.predict_proba(input_data)[0, 1]

# 7. Get Flask API prediction
response = requests.post(
    "http://127.0.0.1:5000/predict",
    json=applicant
)

print("\n--- DIRECT MODEL ---")
print("Probability:", round(float(direct_probability), 4))

print("\n--- FLASK API ---")
print("Status Code:", response.status_code)
print("Response:", response.json())

if response.status_code == 200:
    api_probability = response.json()["default_probability"]

    print("\n--- CONSISTENCY CHECK ---")
    print("Direct model:", round(float(direct_probability), 4))
    print("Flask API:", api_probability)

    if abs(float(direct_probability) - api_probability) < 0.0001:
        print("SUCCESS: Predictions match!")
    else:
        print("MISMATCH: Predictions do not match.")