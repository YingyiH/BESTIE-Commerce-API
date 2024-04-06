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
from msg_db_create import MsgCreate
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

def process_messages():
    '''
    TODO: This is a function to process Kafka messages
          (Kafka server as a receiver receives data and sends it to database)
    '''

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

    if current_retry == MAX_RETRIES:
        LOGGER.error("Max retries reached. Exiting.")
        return

    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        LOGGER.info(f"Received message from consumer {msg}")
        event_code = msg["event_code"]
        process_message(event_code)
        consumer.commit_offsets()

def process_message(event_code):
    print(f"THIS IS MSG CODE: {event_code}")
    if event_code:
        old_data = read_data(event_code)
        write_data(old_data)

def read_data(msg_code):
    
    data = None

    print(f"READING DATA -> THIS IS MSG CODE: {msg_code}")
    with Session(engine) as session:
        data = session.query(MsgCreate).order_by(MsgCreate.last_updated.desc()).first()
    if data is None:
        data = {
            'msg_code': msg_code,
            'msg_string': 'no message',
            'last_updated': datetime.fromtimestamp(0)
        } 
        print(f"THIS IS DATA ITEM: {data}")
    else:
        print(f"THIS IS DATA ITEM: {data}")
        LOGGER.info(f"Received msg code: {msg_code}")
    return data


def write_data(body):
    with Session(engine) as session:
        # Check if the record with the same message code exists
        query = session.query(MsgCreate).filter(MsgCreate.msg_code == body['msg_code']).first()
        query.msg_id = str(uuid4())
        print(f"THIS IS EXISTING RECORD MSG CODE: {body.msg_code}")
        # body['msg_id'] = str(uuid4())
        # If the record exists, update the event_num column
        # existing_record.event_num += 1
        # existing_record.msg_string = f'{existing_record.msg_code} Events Logged: {existing_record.event_num}'
        event_num = body.scalar()
        body.msg_string = f"{body.msg_code} Events Logged: {event_num}"

        data = MsgCreate(
            body.msg_id,
            body.msg_code,
            body.msg_string
        )
        print(f'THIS IS DATA: {data}')
        session.add(data)
        session.commit()

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