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
from models import Msg
from datetime import datetime
from uuid import uuid4
import json

# Define configration settings by configuration file: -------------------------
LOGGER, LOG_CONFIG_FILE = load_log_conf()
DATA, EVENT, RETRY, DEFAULT, APP_CONFIG_FILE  = load_app_conf()

# KAFKA HOST VARIABLES
KAFKA_HOST = EVENT['hostname']
KAFKA_HOST_PORT = EVENT['port']
EVENT_LOGGER_TOPIC = EVENT['topic']
# KAFKA RETRY VARIABLES
MAX_RETRIES = RETRY['max_retry']
RETRY_DELAY_SECONDS = RETRY['delay_seconds']

CONFIG_VALUE = DEFAULT['config_value']



def get_msg():
    """ This is the endpoint that returns
    {
    "0001": int,
    "0002": int,
    "0003": int,
    "0004": int,
    }
    """
    msgs = None

    with Session(engine) as session:
        # Get all messages and add them up
        msgs = session.query(Msg).all()
    
    # Default response if no messages

    response = {
        "0001": 0,
        "0002": 0,
        "0003": 0,
        "0004": 0
    }

    if msgs:
        for msg in msgs:
            response[str(msg.code)] += 1
    
    return response, 201




def process_message(msg):
    msg = Msg(
        id=str(uuid.uuid4()),
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
            process_message(msg)
            consumer.commit_offsets()
            LOGGER.info("Succesfully stored msg to database")
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
    app.run(host="0.0.0.0",port=8120) #nosec