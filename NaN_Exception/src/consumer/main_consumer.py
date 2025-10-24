import redis
import json
import psycopg2
import os
from decimal import Decimal
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

print("Esperando mensajes en Redis...")

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
            print("Nuevo mensaje recibido de Redis. Leyendo último registro de raw_weather_data...")

            cur.execute("""
                SELECT RAW_JSON, TIMESTAMP
                FROM raw_weather_data
                ORDER BY TIMESTAMP DESC
                LIMIT 1
            """)
            row = cur.fetchone()

            if not row:
                print("No hay registros en raw_weather_data todavía.")
                continue

            raw_json, ts = row
            data = json.loads(raw_json)

            latitude = Decimal(str(data.get("latitude", 0)))
            longitude = Decimal(str(data.get("longitude", 0)))
            temperature = Decimal(str(data.get("temperature_2m", 0)))
            humidity = Decimal(str(data.get("relative_humidity_2m", 0)))
            wind_speed = Decimal(str(data.get("wind_speed_10m", 0)))
            cloud_cover = Decimal(str(data.get("cloud_cover", 0)))

            insert_query = """
                INSERT INTO weather_data (
                    LATITUDE, LONGITUDE, TEMPERATURE,
                    RELATIVE_HUMIDITY, WIND_SPEED, CLOUD_COVER, TIMESTAMP
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (latitude, longitude, temperature, humidity, wind_speed, cloud_cover, ts)
            cur.execute(insert_query, values)
            conn.commit()

            print(f"Registro insertado en weather_data con timestamp {ts}\n")

        except Exception as e:
            print("Error al procesar el mensaje:", e)
            conn.rollback()
