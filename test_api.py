import requests
import pandas as pd

# Load dataset
df = pd.read_csv("data/raw/application_train.csv")

# Select one applicant
applicant = df.drop(columns=["TARGET", "SK_ID_CURR"]).iloc[0].to_dict()

# Convert NaN values to None
# None becomes JSON null
applicant = {
    key: None if pd.isna(value) else value
    for key, value in applicant.items()
}

# Send applicant data to Flask API
response = requests.post(
    "http://127.0.0.1:5000/predict",
    json=applicant
)

print("Status Code:", response.status_code)
print("API Response:")
print(response.json())