from pathlib import Path
import os
import joblib
import pandas as pd
from flask import Flask, render_template, request, flash
from dotenv import load_dotenv
from db import load_properties, insert_property
from auth_routes import register_auth_routes

load_dotenv()
ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "house_price_model.joblib"
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-key-change-me")

FEATURES = ["city", "locality", "area_sqft", "bedrooms", "bathrooms",
            "property_type", "furnishing", "parking", "age_years"]
CITIES = ["Bengaluru", "Delhi", "Ghaziabad", "Hyderabad", "Kolkata", "Mumbai", "Noida", "Pune"]
PROPERTY_TYPES = ["Apartment", "Independent House", "Villa"]
FURNISHING = ["Unfurnished", "Semi-Furnished", "Furnished"]

def get_model_bundle():
    if not MODEL_PATH.exists():
        from train_model import main
        main()
    return joblib.load(MODEL_PATH)

def money(value):
    return "₹{:,.0f}".format(float(value))

@app.context_processor
def inject_helpers():
    return {"money": money}

@app.route("/")
def index():
    props = load_properties()
    return render_template("index.html", cities=CITIES, property_types=PROPERTY_TYPES,
                           furnishing_options=FURNISHING, property_count=len(props))

@app.route("/predict", methods=["POST"])
def predict():
    try:
        payload = {
            "city": request.form["city"],
            "locality": request.form["locality"].strip(),
            "area_sqft": int(request.form["area_sqft"]),
            "bedrooms": int(request.form["bedrooms"]),
            "bathrooms": int(request.form["bathrooms"]),
            "property_type": request.form["property_type"],
            "furnishing": request.form["furnishing"],
            "parking": int(request.form["parking"]),
            "age_years": int(request.form["age_years"])
        }
        if not payload["locality"]:
            raise ValueError("Please enter a locality.")
        if not 200 <= payload["area_sqft"] <= 20000:
            raise ValueError("Area must be between 200 and 20,000 sq ft.")
        if not 1 <= payload["bedrooms"] <= 10 or not 1 <= payload["bathrooms"] <= 10:
            raise ValueError("Bedrooms and bathrooms must be between 1 and 10.")
        if payload["age_years"] < 0 or payload["parking"] < 0:
            raise ValueError("Age and parking cannot be negative.")
        bundle = get_model_bundle()
        input_df = pd.DataFrame([payload], columns=FEATURES)
        estimate = max(0, float(bundle["model"].predict(input_df)[0]))
        return render_template("result.html", payload=payload, estimate=estimate,
                               metrics=bundle.get("metrics", {}))
    except (KeyError, ValueError) as exc:
        flash(str(exc) or "Please check your inputs.")
        return render_template("index.html", cities=CITIES, property_types=PROPERTY_TYPES,
                               furnishing_options=FURNISHING, property_count=len(load_properties())), 400

@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    props = load_properties()
    recommendations = None
    filters = {"city": "", "budget": "10000000", "bedrooms": "2",
               "min_area": "500", "property_type": ""}
    if request.method == "POST":
        filters = {k: request.form.get(k, "") for k in filters}
        try:
            budget = float(filters["budget"])
            bedrooms = int(filters["bedrooms"] or 1)
            min_area = int(filters["min_area"] or 0)
            if budget <= 0 or min_area < 0 or bedrooms < 1:
                raise ValueError
            filtered = props.copy()
            if filters["city"]:
                filtered = filtered[filtered["city"] == filters["city"]]
            if filters["property_type"]:
                filtered = filtered[filtered["property_type"] == filters["property_type"]]
            filtered = filtered[
                (filtered["price_inr"] <= budget) &
                (filtered["bedrooms"] >= bedrooms) &
                (filtered["area_sqft"] >= min_area)
            ].copy()
            # Score properties by budget fit, desired size, and bedroom fit.
            filtered["budget_fit"] = 1 - (budget - filtered["price_inr"]) / budget
            filtered["size_fit"] = (filtered["area_sqft"] / max(min_area, 1)).clip(upper=2) / 2
            filtered["match_score"] = (0.65 * filtered["budget_fit"] + 0.35 * filtered["size_fit"]) * 100
            recommendations = filtered.sort_values(
                ["match_score", "price_inr"], ascending=[False, False]
            ).head(12).to_dict(orient="records")
        except (ValueError, TypeError):
            flash("Enter a valid positive budget, bedroom count, and minimum area.")
            recommendations = []
    return render_template("recommend.html", cities=CITIES, property_types=PROPERTY_TYPES,
                           filters=filters, recommendations=recommendations,
                           property_count=len(props))

register_auth_routes(
    app,
    str(ROOT / "users.db"),
    lambda: (CITIES, PROPERTY_TYPES, FURNISHING),
    insert_property,
)

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    # Local development only. Use a production WSGI server for deployment.
    app.run(debug=True)
