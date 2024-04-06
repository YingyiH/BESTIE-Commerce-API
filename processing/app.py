import time
import requests
from connexion import FlaskApp
from load_config import load_log_conf, load_app_conf
from sqlalchemy.orm import Session
from create_datebase import engine, create_database
from stat_create import StatCreate
from datetime import datetime, timedelta
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from data_process import product_processing, review_processing
from models import Stat
from uuid import uuid4
from pykafka import KafkaClient
from pykafka.common import OffsetType 
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
import json

# Define configration settings by configuration file: -------------------------
LOGGER, LOG_CONFIG_FILE = load_log_conf()
SECONDS, EVENT_URL, DEFAULT_COUNT, APP_CONFIG_FILE, EVENT = load_app_conf()

# KAFKA HOST VARIABLES
KAFKA_HOST = EVENT['hostname']
KAFKA_HOST_PORT = EVENT['port']
EVENT_LOGGER_TOPIC = EVENT['topic']
MAX_RETRIES = 5
RETRY_DELAY_SECONDS = 5

LOGGER.info("App Conf File: %s" % APP_CONFIG_FILE )
LOGGER.info("Log Conf File: %s" % LOG_CONFIG_FILE)

producer = None
def kafka_init():
    global producer
    hostname = "%s:%d" % (KAFKA_HOST,KAFKA_HOST_PORT)

    current_retry = 0

    while current_retry < MAX_RETRIES:
        try:
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(EVENT_LOGGER_TOPIC)]
            producer = topic.get_sync_producer()
            LOGGER.info("Connected to Kafka")
            break  # Connection successful, exit the retry loop
        except Exception as e:
            LOGGER.error(f"Failed to connect to Kafka (retry {current_retry + 1}/{MAX_RETRIES}): {e}")
            time.sleep(RETRY_DELAY_SECONDS)
            current_retry += 1

    if current_retry == MAX_RETRIES or producer == None:
        LOGGER.error(f"Max retries reached. Exiting or no consumer {producer}")

# Function to send message to Kafka
def send_message(msg_code):
    global producer

    msg = {
    "event_code": msg_code,
    "datetime" : datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    "payload": "Connected to Kafka"
    }
    msg_str = json.dumps(msg)

    producer.produce(msg_str.encode('utf-8'))


# Populating Statistics: ------------------------------------------------------
def populate_stats():
    try:
        print("BEFORE PROCESSING")
        data = processing()
        print("AFTER PROCESSING")
        write_data(data)

    except Exception as e:
        LOGGER.debug(f"Error processing {e}")
        # LOGGER.error(str(e))

# Initializing Scheduler: -----------------------------------------------------
def init_scheduler():
    
    populate_stats_variables = populate_stats

    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats_variables, 'interval', seconds= SECONDS)
    sched.start()

    return sched, EVENT_URL

SCHEDULED, EVENT_URL = init_scheduler()


# Read Statistics Data: -----------------------------------------------------------------
def read_data():
    data = None

    with Session(engine) as session:
        data = session.query(StatCreate).order_by(
            StatCreate.last_updated.desc()).first()
        
    if data is None:
        return {
            'num_products': 0, 
            'num_reviews': 0, 
            'num_onsale_products': 0, 
            'max_price': 0, 
            'last_updated': datetime.fromtimestamp(0) # datatime.now() - timedelta(100.0)
        }
    else:
        return data.to_dict()
    
# Write Statistics Data: ----------------------------------------------------------------
def write_data(body):

    with Session(engine) as session:
        print("BOOTTYY: ", body)
        body['reading_id'] = str(uuid4())
        data = StatCreate(
            body['reading_id'],
            body['num_products'],
            body['num_reviews'],
            body['num_onsale_products'],
            body['max_price']
        )

        session.add(data)
        session.commit()

# Endpoint to Get Statistics: ------------------------------------------------------------
# def get_stats():
    
#     LOGGER.info('Received product and review event request.')

#     data = read_data()

#     if data['num_products'] <= 0 and data['num_reviews'] <= 0:
#         LOGGER.error('Empty input')
#         return 'Statistics do not exist', 404
#     if data['num_products'] + data['num_reviews'] >= DEFAULT_COUNT:
#         send_message("0004")
    
#     LOGGER.debug(f'GET event requests returns: {data}')
#     LOGGER.info('GET stats request completed')
#     return data, 200

# Processing Events: ----------------------------------------------------------------------
def processing():

    old_data = read_data()
    time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    timestamp_dict = {
        'start_timestamp': old_data['last_updated'].strftime("%Y-%m-%dT%H:%M:%S"),
        'end_timestamp': time
    }

    product_event = requests.get(f'{EVENT_URL}/products', params=timestamp_dict, timeout = 10)
    review_event = requests.get(f'{EVENT_URL}/reviews', params=timestamp_dict, timeout = 10)

    product_data = product_event.json()
    review_data = review_event.json()

    LOGGER.info(f'Received {len(product_data)} products and {len(review_data)} reviews.')

    if (len(product_data) + len(review_data)) >= DEFAULT_COUNT:
        LOGGER.info(f'Received {len(product_data)}. Sent event 0004')
        send_message("0004")
    
    # updates data inplace
    try:
        LOGGER.info(f'{product_data} products and {len(review_data)} reviews')
        product_processing(product_data, old_data)
        review_processing(review_data, old_data)
    except Exception as e:
        LOGGER.error(f'ERROR processing: {str(e)}')

    LOGGER.info("Finished processing")

    LOGGER.debug(f'Updated statistic values: {old_data}')

    return old_data

# App Core Setup: ----------------------------------------------------------------
app = FlaskApp(__name__)

app.add_middleware(
    CORSMiddleware,
    position=MiddlewarePosition.BEFORE_EXCEPTION,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_api("./openai.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    print("NOT YET CREATED DATABASE--------------------------------")
    create_database()
    print("CREATED DATABASE--------------------------------")
    kafka_init()
    send_message("0003")
    # run our standalone gevent server
    init_scheduler()
    app.run(host="0.0.0.0" ,port=8100) #nosec