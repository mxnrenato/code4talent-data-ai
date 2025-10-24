from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import psycopg2
from decimal import Decimal
from datetime import datetime

app = FastAPI()

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_DB = os.getenv("POSTGRES_DB", "climate_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "administrator")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "hackathon2025")

def get_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )

def safe_convert(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return value

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/series")
async def get_latest_records():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM weather_data
                    LIMIT 50;
                """)
                rows = cur.fetchall()
                columns = [desc[0] for desc in cur.description]

                data = [
                    {col: safe_convert(val) for col, val in zip(columns, row)}
                    for row in rows
                ]

        return JSONResponse(content={"count": len(data), "records": data})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
