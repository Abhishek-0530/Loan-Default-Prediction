from flask import Flask, request, jsonify, render_template
from pathlib import Path
import sys


# ============================================================
# Project Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

sys.path.insert(
    0,
    str(BASE_DIR / "src")
)


# ============================================================
# Import Prediction Function
# ============================================================

from predict import predict_loan_risk


# ============================================================
# Create Flask App
# ============================================================

app = Flask(__name__)


# ============================================================
# Home Page
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ============================================================
# Prediction API
# ============================================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        applicant_data = request.get_json()


        # ----------------------------------------------------
        # Check whether data was received
        # ----------------------------------------------------

        if not applicant_data:

            return jsonify({
                "error": "No applicant data provided"
            }), 400


        # ----------------------------------------------------
        # Run prediction
        # ----------------------------------------------------

        result = predict_loan_risk(
            applicant_data
        )


        return jsonify(result), 200


    # --------------------------------------------------------
    # Validation errors
    # --------------------------------------------------------

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400


    # --------------------------------------------------------
    # Unexpected server errors
    # --------------------------------------------------------

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# Run Flask Application
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )