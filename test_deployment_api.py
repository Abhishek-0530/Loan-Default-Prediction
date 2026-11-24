import requests


applicant = {
    "AMT_INCOME_TOTAL": 180000,
    "AMT_CREDIT": 500000,
    "AMT_ANNUITY": 25000,
    "AMT_GOODS_PRICE": 450000,

    "EXT_SOURCE_1": 0.60,
    "EXT_SOURCE_2": 0.55,
    "EXT_SOURCE_3": 0.65,

    "AGE_YEARS": 30,
    "EMPLOYED_YEARS": 5,

    "NAME_CONTRACT_TYPE": "Cash loans",
    "NAME_EDUCATION_TYPE": "Higher education",
    "NAME_INCOME_TYPE": "Working",
    "OCCUPATION_TYPE": "Laborers",
    "NAME_FAMILY_STATUS": "Married",
    "FLAG_OWN_CAR": "Y",

    "DEF_30_CNT_SOCIAL_CIRCLE": 0,
    "DEF_60_CNT_SOCIAL_CIRCLE": 0,
    "REGION_RATING_CLIENT": 2
}


response = requests.post(
    "http://127.0.0.1:5000/predict",
    json=applicant
)


print("Status Code:", response.status_code)

print("\nAPI Response:")

try:
    print(response.json())
except Exception:
    print(response.text)
