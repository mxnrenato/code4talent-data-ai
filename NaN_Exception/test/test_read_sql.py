import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_DB = os.getenv("POSTGRES_DB", "climate_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "administrator")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "hackathon2025")

try:
    print(f"Conectando a PostgreSQL en {POSTGRES_HOST}:{POSTGRES_PORT} ...")
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )
    print("Conexión exitosa.\n")

    cur = conn.cursor()
    cur.execute("SELECT * FROM weather_data LIMIT 5;")

    rows = cur.fetchall()
    print("Últimos 5 registros:")
    for row in rows:
        print(row)

    cur.close()
    conn.close()
    print("\n🔒 Conexión cerrada correctamente.")

except psycopg2.Error as e:
    print("Error al conectar o ejecutar el SELECT:")
    print(e)
