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
KAFKA_TOPIC = EVENT['topic']
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
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(KAFKA_TOPIC)]
    LOGGER.info("Connected to Kafka")

    current_retry = 0
    while current_retry < MAX_RETRIES:
        try:
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(KAFKA_TOPIC)]
            LOGGER.info("Connected to Kafka")
            break  # Connection successful, exit the retry loop
        except Exception as e:
            LOGGER.error(f"Failed to connect to Kafka (retry {current_retry + 1}/{MAX_RETRIES}): {e}")
            time.sleep(RETRY_DELAY_SECONDS)
            current_retry += 1

    if current_retry == MAX_RETRIES:
        LOGGER.error("Max retries reached. Exiting.")
        return
    
    consumer = topic.get_simple_consumer(consumer_group=b'event_group', reset_offset_on_start=False, auto_offset_reset=OffsetType.LATEST)

    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg_data = json.loads(msg_str)
        process_message(msg_data)
        consumer.commit_offsets()

def process_message(msg_data):
    event_type = msg_data.get('event_type')
    if event_type:
        tb = get_event(event_type)
        write_data(tb)

def get_event(event_type):
    # Default values
    tb = {
        'msg_id': str(uuid4()),
        'msg_code': 'x',
        'event_num': 0,
        'msg_string': 'no message'
    }

    if event_type == 'receiver':
        tb['msg_code'] = '0001'
    elif event_type == 'storage':
        tb['msg_code'] = '0002'
    elif event_type == 'processor_startup':
        tb['msg_code'] = '0003'
    elif event_type == 'processor_more':
        tb['msg_code'] = '0004'

    LOGGER.info(f"Received event type: {event_type}, Message Code: {tb['msg_code']}")
    return tb

def write_data(tb):
    with Session(engine) as session:
        # Check if the record with the same message code exists
        existing_record = session.query(MsgCreate).filter(MsgCreate.msg_code == tb['msg_code']).first()
        if existing_record:
            # If the record exists, update the event_num column
            existing_record.event_num += 1
            existing_record.msg_string = f'{existing_record.msg_code} Events Logged: {existing_record.event_num}'
        else:
            # If the record doesn't exist, create a new record
            data = MsgCreate(tb)
            session.add(data)
        session.commit()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openai.yaml", strict_validation=True, validate_responses=True)

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