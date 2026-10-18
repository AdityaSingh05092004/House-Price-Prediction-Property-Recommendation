"""Database helpers. SQLite is the zero-configuration default; MySQL is optional."""
import os
import sqlite3
from pathlib import Path
from urllib.parse import urlparse
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///properties.db")

def _sqlite_path():
    if DATABASE_URL.startswith("sqlite:///"):
        return ROOT / DATABASE_URL.replace("sqlite:///", "", 1)
    return ROOT / "properties.db"

def get_mysql_connection():
    import pymysql
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "house_price_db"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

def init_db():
    if DATABASE_URL == "mysql":
        conn = get_mysql_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS properties (
                        property_id VARCHAR(32) PRIMARY KEY,
                        city VARCHAR(100), locality VARCHAR(100), area_sqft INT,
                        bedrooms INT, bathrooms INT, property_type VARCHAR(100),
                        furnishing VARCHAR(100), parking INT, age_years INT,
                        price_inr BIGINT
                    )
                """)
        finally:
            conn.close()
    else:
        path = _sqlite_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS properties (
                    property_id TEXT PRIMARY KEY, city TEXT, locality TEXT,
                    area_sqft INTEGER, bedrooms INTEGER, bathrooms INTEGER,
                    property_type TEXT, furnishing TEXT, parking INTEGER,
                    age_years INTEGER, price_inr INTEGER
                )
            """)
            conn.commit()

def seed_properties():
    """Load bundled demo CSV only if the properties table is empty."""
    csv_path = ROOT / "data" / "properties.csv"
    df = pd.read_csv(csv_path)
    init_db()
    if DATABASE_URL == "mysql":
        conn = get_mysql_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS n FROM properties")
                count = cur.fetchone()["n"]
                if count == 0:
                    sql = """INSERT INTO properties
                    (property_id,city,locality,area_sqft,bedrooms,bathrooms,property_type,
                    furnishing,parking,age_years,price_inr)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                    cur.executemany(sql, [tuple(x) for x in df.itertuples(index=False, name=None)])
        finally:
            conn.close()
    else:
        with sqlite3.connect(_sqlite_path()) as conn:
            count = conn.execute("SELECT COUNT(*) FROM properties").fetchone()[0]
            if count == 0:
                df.to_sql("properties", conn, if_exists="append", index=False)

def load_properties():
    seed_properties()
    if DATABASE_URL == "mysql":
        conn = get_mysql_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM properties")
                return pd.DataFrame(cur.fetchall())
        finally:
            conn.close()
    with sqlite3.connect(_sqlite_path()) as conn:
        return pd.read_sql_query("SELECT * FROM properties", conn)
