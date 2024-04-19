# Yingyi He (Set B) A01230375

import uuid
from connexion import NoContent
import connexion
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
from threading import Thread
from pykafka import KafkaClient
from pykafka.common import OffsetType 
from sqlalchemy.orm import Session
from create_database import create_database, engine
import time
from load_config import load_log_conf, load_app_conf
from models import Anomaly
from datetime import datetime
from uuid import uuid4
import json

# Define configration settings by configuration file: -------------------------
LOGGER, LOG_CONFIG_FILE = load_log_conf()
DATA, EVENT, RETRY, DEFAULT_ANOMALY, APP_CONFIG_FILE  = load_app_conf()

# KAFKA HOST VARIABLES
KAFKA_HOST = EVENT['hostname']
KAFKA_HOST_PORT = EVENT['port']
EVENT_LOGGER_TOPIC = EVENT['topic']
# KAFKA RETRY VARIABLES
MAX_RETRIES = RETRY['max_retry']
RETRY_DELAY_SECONDS = RETRY['delay_seconds']

MAX_PRICE = DEFAULT_ANOMALY['product_anomaly']['max_price']
MIN_PRICE = DEFAULT_ANOMALY['product_anomaly']['min_price']

MAX_RATE = DEFAULT_ANOMALY['review_anomaly']['max_rate']
MIN_RATE = DEFAULT_ANOMALY['review_anomaly']['min_rate']

# ------------------------------------------------------------------------------------------------

# Endpoint implementations
def add_product_anomaly():

    try:
        price = int(msg['anomaly_value'])

    except (KeyError, ValueError, TypeError):
        LOGGER.error("Invalid product information")
        return NoContent, 400

    if price > MAX_PRICE or price < MIN_PRICE:

        msg = Anomaly(
                id=str(uuid.uuid4()),
                event_id=str(msg['event_id']),
                trace_id=str(msg['trace_id']),
                anomaly_type=str(msg['anomaly_type']),
                description=str('This is an product info anomaly data payload.'),
                date=datetime.now()
            )

        with Session(engine) as session:
            session.add(msg)
            session.commit()

        LOGGER.debug(f'Added event "product anomaly" request with a id of {id}')

    return NoContent, 201

# ------------------------------------------------------------------------------------------------

# Endpoint implementations
def add_review_anomaly():

    try:
        rate = int(msg['anomaly_value'])

    except (KeyError, ValueError, TypeError):
        LOGGER.error("Invalid product review")
        return NoContent, 400

    if rate > MAX_RATE or rate < MIN_RATE:

        msg = Anomaly(
                id=str(uuid.uuid4()),
                event_id=str(msg['event_id']),
                trace_id=str(msg['trace_id']),
                anomaly_type=str(msg['anomaly_type']),
                description=str('This is an product reivew anomaly data payload.'),
                date=datetime.now()
            )

        with Session(engine) as session:
            session.add(msg)
            session.commit()

        LOGGER.debug(f'Added event "product anomaly" request with a id of {id}')

    return NoContent, 201

# ------------------------------------------------------------------------------------------------

def process_message(msg):
    msg = Anomaly(
        id=int(uuid.uuid4()),
        event_id = str(msg['trace_id']),
        event_type = str(msg['event_type']),
        code=str(msg['event_code']),
        message=str(msg['payload']),
        date=datetime.now()
    )

    with Session(engine) as session:
        session.add(msg)
        session.commit()

def process_messages():
    hostname = "%s:%d" % (KAFKA_HOST,KAFKA_HOST_PORT)

    current_retry = 0
    consumer = None

    while current_retry < MAX_RETRIES:
        try:
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(EVENT_LOGGER_TOPIC)]
            consumer = topic.get_simple_consumer(consumer_group=b'event_group', reset_offset_on_start=False, auto_offset_reset=OffsetType.LATEST)
            LOGGER.info("Connected to Kafka")
            break  # Connection successful, exit the retry loop
        except Exception as e:
            LOGGER.error(f"Failed to connect to Kafka (retry {current_retry + 1}/{MAX_RETRIES}): {e}")
            time.sleep(RETRY_DELAY_SECONDS)
            current_retry += 1

    if current_retry == MAX_RETRIES or consumer == None:
        LOGGER.error(f"Max retries reached. Exiting or no consumer {consumer}")
        return

    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        LOGGER.info(f"Received message from consumer {msg}")
        try:
            if msg["anomaly_type"] == "product_anomaly":
                add_product_anomaly()
                LOGGER.info("Added product_anomaly")
            elif msg["anomaly_type"] == "review_anomaly":
                add_review_anomaly()
                LOGGER.info("Added review anomaly")
            consumer.commit_offsets()
            LOGGER.info("Succesfully stored event to database")
        except Exception as e:
            LOGGER.error(str(e))


# --------------------------------------------------------------------------------------------------------------------
app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openai.yml", strict_validation=True, validate_responses=True)

app.add_middleware(
    CORSMiddleware,
    position=MiddlewarePosition.BEFORE_EXCEPTION,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    create_database()
    t1 = Thread(target=process_messages)
    t1.daemon = True
    t1.start()
    app.run(host="0.0.0.0",port=80) #nosec