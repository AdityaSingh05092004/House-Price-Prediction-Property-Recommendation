"""Train and evaluate the updated Random Forest house-price model.

Uses the feature schema and RandomizedSearchCV strategy from untitled11.py,
then saves a complete preprocessing + model bundle for the Flask application.
"""
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, RandomizedSearchCV
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
    missing = sorted(set(FEATURES + [TARGET]) - set(df.columns))
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")
    df[TARGET] = pd.to_numeric(df[TARGET], errors="raise")
    df = df.dropna(subset=[TARGET]).copy()
    if len(df) < 10:
        raise ValueError("At least 10 usable rows are required to train the model.")

    X, y = df[FEATURES], df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )
    pipeline = Pipeline([
        ("preprocessor", build_preprocessor()),
        ("regressor", RandomForestRegressor(random_state=42, n_jobs=-1)),
    ])
    param_grid = {
        "regressor__n_estimators": [150, 250, 350],
        "regressor__max_depth": [None, 10, 20, 30, 40],
        "regressor__min_samples_split": [2, 5, 10],
        "regressor__min_samples_leaf": [1, 2, 4],
        "regressor__max_features": [1.0, 0.7, "sqrt"],
    }
    search = RandomizedSearchCV(
        estimator=pipeline,
        param_distributions=param_grid,
        n_iter=6,
        cv=3,
        scoring="neg_root_mean_squared_error",
        random_state=42,
        n_jobs=1,
        verbose=1,
    )
    print("Starting Random Forest hyperparameter search...")
    search.fit(X_train, y_train)
    best_model = search.best_estimator_
    predictions = best_model.predict(X_test)
    metrics = {
        "mae_inr": round(float(mean_absolute_error(y_test, predictions)), 2),
        "rmse_inr": round(float(np.sqrt(mean_squared_error(y_test, predictions))), 2),
        "r2": round(float(r2_score(y_test, predictions)), 4),
        "training_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "model_name": "RandomForestRegressor",
        "best_parameters": search.best_params_,
    }
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": best_model, "features": FEATURES, "metrics": metrics}, MODEL_PATH)
    print("\n========== MODEL EVALUATION ==========")
    for key, value in metrics.items():
        print(f"{key}: {value}")
    print(f"\nModel bundle saved to: {MODEL_PATH}")
    return metrics


if __name__ == "__main__":
    main()
