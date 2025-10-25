from api_call import data_call
import redis
import json
import time
import os
from dotenv import load_dotenv
from log_util.logger_config import setup_logger

logger = setup_logger(__name__, "main_producer.log")

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_CHANNEL = "weather_channel"

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def main():
    while True:
        try:
            data = data_call()
            if data:
                r.publish(REDIS_CHANNEL, json.dumps(data))
                logger.info("Mensaje publicado en Redis.")
                logger.debug(f"Contenido del mensaje: {data}")
        except Exception as e:
            logger.error(f"Error durante la ejecución: {e}")
        time.sleep(15)

if __name__ == "__main__":
    main()
