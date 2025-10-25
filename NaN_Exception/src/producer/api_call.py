import requests
import logging
from datetime import datetime
from log_util.logger_config import setup_logger

url = "https://api.open-meteo.com/v1/forecast?latitude=-0.2298&longitude=-78.525&current=temperature_2m,relative_humidity_2m,wind_speed_10m,cloud_cover&timezone=America%2FNew_York&forecast_days=1"

logger = setup_logger(__name__, "api_call.log")

def data_call():
    try:
        logger.info("Request a Open Meteor...")
        response = requests.get(url)
        data = response.json()
        
        logger.info("Obteniendo información lat y lon...")
        information_column = {
            'latitude': data['latitude'],
            'longitude': data['longitude']
        }

        values_column = {
            'temperature_2m': data['current']['temperature_2m'],
            'relative_humidity_2m': data['current']['relative_humidity_2m'],
            'wind_speed_10m': data['current']['wind_speed_10m'],
            'cloud_cover': data['current']['cloud_cover']
        }
        logger.info("Generación de Timestamp...")
        appended_columns = {
            **information_column,
            **values_column,
            'timestamp': datetime.now().isoformat()
        }

        print(appended_columns)
        return appended_columns

    except Exception as e:
        logging.error(f"API call failed: {e}")
        return None
