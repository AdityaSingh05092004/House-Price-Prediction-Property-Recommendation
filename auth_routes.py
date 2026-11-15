"""Login + add-property routes for GrihaMool.

Users live in their own small SQLite file (db_path). New properties are
saved through the insert_property(dict) callback, which should write to the
same place db.load_properties() reads from.
"""
import sqlite3
from functools import wraps

from flask import flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


PROPERTY_FIELDS = ["city", "locality", "price_inr", "area_sqft", "bedrooms",
                   "bathrooms", "property_type", "furnishing", "parking", "age_years"]


def register_auth_routes(app, db_path, get_options, insert_property):
    def db():
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    with db() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "username TEXT UNIQUE NOT NULL,"
            "password_hash TEXT NOT NULL)"
        )

    def login_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("user"):
                flash("Please log in first.")
                return redirect(url_for("login", next=request.path))
            return view(*args, **kwargs)
        return wrapped

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            if len(username) < 3 or len(password) < 6:
                flash("Username needs 3+ characters and password 6+.")
            elif password != request.form.get("confirm"):
                flash("Passwords do not match.")
            else:
                try:
                    with db() as conn:
                        conn.execute(
                            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                            (username, generate_password_hash(password)),
                        )
                    flash("Account created. Please log in.")
                    return redirect(url_for("login"))
                except sqlite3.IntegrityError:
                    flash("That username is already taken.")
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            with db() as conn:
                row = conn.execute(
                    "SELECT * FROM users WHERE username = ?", (username,)
                ).fetchone()
            if row and check_password_hash(row["password_hash"], request.form.get("password", "")):
                session["user"] = row["username"]
                nxt = request.args.get("next", "")
                return redirect(nxt if nxt.startswith("/") and not nxt.startswith("//") else url_for("index"))
            flash("Invalid username or password.")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been logged out.")
        return redirect(url_for("index"))

    @app.route("/add-property", methods=["GET", "POST"])
    @login_required
    def add_property():
        cities, property_types, furnishing_options = get_options()
        if request.method == "POST":
            f = request.form
            try:
                values = (
                    f["city"].strip(), f["locality"].strip(),
                    int(f["price_inr"]), int(f["area_sqft"]),
                    int(f["bedrooms"]), int(f["bathrooms"]),
                    f["property_type"], f["furnishing"],
                    int(f["parking"]), int(f["age_years"]),
                )
                if values[2] <= 0 or values[3] <= 0 or not values[0] or not values[1]:
                    raise ValueError
            except (KeyError, ValueError):
                flash("Please enter valid property details.")
            else:
                insert_property(dict(zip(PROPERTY_FIELDS, values)))
                flash("Property added successfully.")
                return redirect(url_for("recommend"))
        return render_template(
            "add_property.html", cities=cities,
            property_types=property_types, furnishing_options=furnishing_options,
        )
