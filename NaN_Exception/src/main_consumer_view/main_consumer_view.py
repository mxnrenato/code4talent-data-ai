import redis
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_DB = os.getenv("POSTGRES_DB", "climate_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "administrator")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "hackathon2025")
REDIS_CHANNEL = "weather_channel"

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
pubsub = r.pubsub()
pubsub.subscribe(REDIS_CHANNEL)

print("Esperando mensajes...")

try:
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )
    cur = conn.cursor()
except Exception as e:
    print("Error al conectar con PostgreSQL:", e)
    exit()

for message in pubsub.listen():
    if message["type"] == "message":
        try:
            print("Leyendo último registro de weather_data...")
            cur.execute("""
                SELECT
                LATITUDE, LONGITUDE, TEMPERATURE,
                RELATIVE_HUMIDITY, WIND_SPEED, CLOUD_COVER, TIMESTAMP
                FROM weather_data
                ORDER BY TIMESTAMP DESC
                LIMIT 1
            """)
            row = cur.fetchone()
            if not row:
                print("No hay registros en weather_data todavía.")
                continue

            latitude, longitude, temperature, humidity, wind_speed, cloud_cover, ts = row

            cur.execute("""
            INSERT INTO weather_data_view (
                LATITUDE, LONGITUDE, DATE, HOUR,
                AVG_TEMPERATURE, AVG_HUMIDITY, AVG_WIND_SPEED, AVG_CLOUD_COVER
            )
            SELECT
               latitude, longitude,
                cast(timestamp AS DATE) Date,
                EXTRACT(HOUR FROM timestamp) AS HOUR,
                AVG(TEMPERATURE),
                AVG(RELATIVE_HUMIDITY),
                AVG(WIND_SPEED),
                AVG(CLOUD_COVER),
                AVG(temperature) OVER (ORDER BY EXTRACT(HOUR FROM timestamp) ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS mm_temp
            FROM weather_data
            GROUP BY latitude, longitude, timestamp,cast(timestamp AS DATE), EXTRACT(HOUR FROM timestamp);""", (latitude, longitude, ts, ts, ts, latitude, longitude, ts, ts, latitude, longitude))

            conn.commit()
            print(f"Registro insertado en weather_data_view con timestamp {ts}\n")

        except Exception as e:
            print("Error al procesar el mensaje:", e)
            conn.rollback()

 