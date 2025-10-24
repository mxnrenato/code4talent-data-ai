from api_call import data_call
import redis
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_CHANNEL = "weather_channel"

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def main():
    while True:
        data = data_call()
        if data:
            r.publish(REDIS_CHANNEL, json.dumps(data))
            print("Mensaje publicado en Redis.")
        time.sleep(15)

if __name__ == "__main__":
    main()
