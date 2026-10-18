"""Validated prediction helpers shared by the Flask app and tests."""
from pathlib import Path
import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "house_price_model.joblib"
FEATURES = ["city", "locality", "area_sqft", "bedrooms", "bathrooms",
            "property_type", "furnishing", "parking", "age_years"]


def load_model_bundle():
    """Load a trained model bundle, training it on first use if necessary."""
    if not MODEL_PATH.exists():
        from src.train_model import main
        main()
    return joblib.load(MODEL_PATH)


def validate_payload(payload):
    """Validate a normalized property dictionary before inference."""
    required = FEATURES
    missing = [key for key in required if key not in payload]
    if missing:
        raise ValueError(f"Missing property fields: {', '.join(missing)}")
    locality = str(payload["locality"]).strip()
    if not locality:
        raise ValueError("Please enter a locality.")
    try:
        area = int(payload["area_sqft"])
        bedrooms = int(payload["bedrooms"])
        bathrooms = int(payload["bathrooms"])
        parking = int(payload["parking"])
        age = int(payload["age_years"])
    except (TypeError, ValueError) as exc:
        raise ValueError("Area, bedrooms, bathrooms, parking and age must be whole numbers.") from exc
    if not 200 <= area <= 20000:
        raise ValueError("Area must be between 200 and 20,000 sq ft.")
    if not 1 <= bedrooms <= 10 or not 1 <= bathrooms <= 10:
        raise ValueError("Bedrooms and bathrooms must be between 1 and 10.")
    if parking < 0 or age < 0:
        raise ValueError("Age and parking cannot be negative.")
    normalized = dict(payload)
    normalized.update({
        "locality": locality, "area_sqft": area, "bedrooms": bedrooms,
        "bathrooms": bathrooms, "parking": parking, "age_years": age,
    })
    return normalized


def predict_price(payload, bundle=None):
    """Return a non-negative estimate and model metrics for a property payload."""
    normalized = validate_payload(payload)
    bundle = bundle or load_model_bundle()
    feature_order = bundle.get("features", FEATURES)
    row = pd.DataFrame([{key: normalized[key] for key in feature_order}], columns=feature_order)
    estimate = max(0.0, float(bundle["model"].predict(row)[0]))
    return estimate, bundle.get("metrics", {})
