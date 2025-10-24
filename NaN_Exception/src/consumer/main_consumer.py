import redis
import json
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
    if message['type'] == 'message':
        try:
            data = json.loads(message['data'])
            print(f"Mensaje recibido: {data}")

            insert_query = """
                INSERT INTO weather_data (
                    LATITUDE, LONGITUDE, TEMPERATURE,
                    RELATIVE_HUMIDITY, WIND_SPEED, CLOUD_COVER, TIMESTAMP
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                data['latitude'],
                data['longitude'],
                data['temperature_2m'],
                data['relative_humidity_2m'],
                data['wind_speed_10m'],
                data['cloud_cover'],
                data['timestamp']
            )

            cur.execute(insert_query, values)
            conn.commit()
            print("Datos insertados en PostgreSQL.\n")

        except Exception as e:
            print(f"Error al procesar el mensaje: {e}")
