# GrihaMool — Har Ghar Ki Sahi Keemat
 
House Price Prediction & Property Recommendation: a full-stack academic project with house-price regression, preference-based property recommendations, user accounts, a Flask UI, and SQLite/MySQL storage.
 
## Features
- Estimate a property's price from city, locality, area, bedrooms, bathrooms, type, furnishing, parking and age. The result is shown as a **price range** (about ±5% around the model estimate, rounded to the nearest lakh).
- Train/evaluate an Extra Trees regression model with scikit-learn.
- Show MAE, RMSE and R² on the prediction result.
- Recommend and rank listings by budget, city, minimum bedrooms, minimum area and property type.
- **User accounts:** register, log in and log out (passwords are stored hashed, never in plain text).
- **Add Property:** logged-in users can add a new property with its price; it appears in Find Properties straight away.
- Store listings in SQLite by default; optional MySQL support.
- Responsive UI and input validation.
## Important data disclaimer
`data/properties.csv` is **synthetic demo data**, generated to make the project runnable immediately. It is not actual property listings and must not be used for real property valuation. Replace it with a licensed, verified dataset before making real-world claims. The reported model metrics measure performance on this synthetic dataset only.
 
Properties added through the Add Property page are saved to the listings database and used by the recommender. They do **not** change the price model until it is retrained (see "Retraining with new properties").
 
## Requirements
- Python 3.10 or newer recommended
- pip
- MySQL is optional (SQLite is the default)
## Setup on Windows (PowerShell)
```powershell
# 1. Extract this ZIP and open the project folder in VS Code
# 2. Create a virtual environment
py -m venv .venv
 
# 3. Activate it
.\.venv\Scripts\Activate.ps1
 
# If PowerShell blocks activation, run this for the current terminal only:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# Then activate again.
 
# 4. Install packages
python -m pip install --upgrade pip
pip install -r requirements.txt
 
# 5. Create environment file
Copy-Item .env.example .env
 
# 6. Train the model and print evaluation metrics
python train_model.py
 
# 7. Start the app
python app.py
```
Open the local address printed in the terminal (normally `http://127.0.0.1:5000`).
 
## macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python train_model.py
python app.py
```
 
## Using the website
1. **Price Predictor** (home page): enter the property details to get a likely price range.
2. **Find Properties:** set your budget, city, bedrooms, minimum area and type to see ranked matches.
3. **Register / Login:** create an account at `/register`, then log in at `/login`.
4. **Add Property:** once logged in, open Add Property from the menu, fill in the details and price, and save.
## Environment settings
Set a long random secret in `.env` so login sessions are secure:
```env
FLASK_SECRET_KEY=replace-with-a-long-random-secret
```
The app falls back to a placeholder key if this is missing, which is fine for local testing only.
 
## Optional MySQL setup
1. Start MySQL and run `schema.sql` in MySQL Workbench.
2. Edit `.env`:
```env
DATABASE_URL=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=house_price_db
FLASK_SECRET_KEY=replace-with-a-long-random-secret
```
3. Stop and restart the app. On first run, the demo CSV seeds an empty `properties` table.
4. Do not commit `.env` or real credentials to GitHub.
User accounts are always stored in a small local SQLite file (`users.db`), even when listings use MySQL.
 
## Dataset columns
| Column | Meaning |
|---|---|
| `property_id` | Unique listing ID (added properties get an ID starting with `U`) |
| `city`, `locality` | Location features |
| `area_sqft` | Built-up area in square feet |
| `bedrooms`, `bathrooms` | Room counts |
| `property_type` | Apartment, Independent House, Villa |
| `furnishing` | Unfurnished, Semi-Furnished, Furnished |
| `parking` | Parking spaces |
| `age_years` | Approximate property age |
| `price_inr` | Target variable, Indian rupees |
 
## Project structure
```text
House-Price-Prediction-Property-Recommendation/
├── app.py                  # Flask routes: predict, recommend, about
├── auth_routes.py          # register, login, logout, add property
├── db.py                   # database helpers (load_properties, insert_property)
├── train_model.py
├── requirements.txt
├── .env.example
├── schema.sql
├── users.db                # created automatically on first run
├── properties.db           # created automatically (SQLite default)
├── data/
│   └── properties.csv
├── models/                 # trained model saved here
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── result.html
│   ├── recommend.html
│   ├── about.html
│   ├── login.html
│   ├── register.html
│   └── add_property.html
└── static/
    └── style.css
```
Add `users.db`, `properties.db` and `.env` to `.gitignore` so they are not uploaded to GitHub.
 
## Model workflow
1. Load the CSV with Pandas.
2. Split features and target into training and test sets.
3. Impute missing categorical/numeric values.
4. One-hot encode categorical variables and scale numeric variables.
5. Train `ExtraTreesRegressor`.
6. Evaluate using MAE, RMSE and R².
7. Save the fitted preprocessing + model pipeline using Joblib.
8. Load it in Flask and predict from validated form input.
9. Show the prediction as a range (estimate × 0.95 to estimate × 1.05).
## Retraining with new properties
To make the price model learn from properties added on the website, retrain it on the database contents instead of only the CSV, then run `python train_model.py` again. If you change the columns, update `FEATURES`, the preprocessing columns, the database schema and the input forms together.
 
## Recommendation logic
The demo recommender filters listings to the requested budget, city, bedrooms, area and type. The remaining listings are ranked using a simple weighted score (budget fit 65%, area fit 35%). It is a transparent baseline, not a learned ranking model. User-added properties are included automatically.
 
## Suggested final-year improvements
- Replace synthetic data with a real, legally usable dataset and document its source.
- Add exploratory data analysis, outlier handling and baseline model comparison.
- Compare Linear Regression, Random Forest/Extra Trees, Gradient Boosting and XGBoost (optional).
- Add train/validation strategy and feature importance analysis.
- Let users edit and delete their own listings, save favourite properties, and add pagination and admin controls.
- Replace the fixed ±5% range with a data-driven interval (for example from the spread of tree predictions).
- Add unit tests, logging, API endpoints, Docker, deployment and screenshots.
- Consider location-based geospatial features and time-based market changes if the dataset supports them.
## Troubleshooting
- If `python` is not found, try `py` on Windows or `python3` on macOS/Linux.
- If port 5000 is busy, change the final line to `app.run(debug=True, port=5001)`.
- If packages fail to install, confirm that the virtual environment is activated and the Python version is supported.
- If you see `No module named 'auth_routes'`, make sure `auth_routes.py` is in the same folder as `app.py`.
- If you see `block 'title' defined twice`, a template file has duplicated content; each template should have one `{% extends %}`, one title block and one content block.
- If login stops working after a restart, check that `FLASK_SECRET_KEY` in `.env` is set and has not changed.
- If changing the CSV schema, update `FEATURES`, the preprocessing columns, database schema and input forms together.
 