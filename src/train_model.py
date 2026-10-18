"""Train and evaluate the Apna Ghar house-price regression model."""
from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "properties.csv"
MODEL_DIR = ROOT / "models"
MODEL_PATH = MODEL_DIR / "house_price_model.joblib"
FEATURES = ["city", "locality", "area_sqft", "bedrooms", "bathrooms",
            "property_type", "furnishing", "parking", "age_years"]
TARGET = "price_inr"
CATEGORICAL = ["city", "locality", "property_type", "furnishing"]
NUMERIC = [column for column in FEATURES if column not in CATEGORICAL]


def build_preprocessor():
    """Build preprocessing that is fitted only on the training split."""
    return ColumnTransformer([
        ("categorical", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]), CATEGORICAL),
        ("numeric", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]), NUMERIC),
    ])


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    required = set(FEATURES + [TARGET])
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")
    df = df.dropna(subset=[TARGET]).copy()
    if len(df) < 10:
        raise ValueError("At least 10 usable rows are required to train the demo model.")

    X, y = df[FEATURES], pd.to_numeric(df[TARGET], errors="raise")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    model = Pipeline([
        ("preprocessor", build_preprocessor()),
        ("regressor", ExtraTreesRegressor(
            n_estimators=350, min_samples_leaf=2, random_state=42, n_jobs=-1
        )),
    ])
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    metrics = {
        "mae_inr": round(float(mean_absolute_error(y_test, predictions)), 2),
        "rmse_inr": round(float(mean_squared_error(y_test, predictions) ** 0.5), 2),
        "r2": round(float(r2_score(y_test, predictions)), 4),
        "test_rows": int(len(y_test)),
        "training_rows": int(len(X_train)),
        "model_name": "ExtraTreesRegressor",
    }
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "features": FEATURES, "metrics": metrics}, MODEL_PATH)
    print(f"Model saved: {MODEL_PATH}")
    print("Evaluation metrics:")
    for name, value in metrics.items():
        print(f"  {name}: {value}")
    return metrics


if __name__ == "__main__":
    main()
