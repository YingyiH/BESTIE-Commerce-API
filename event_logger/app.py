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
    print(f'THIS IS EVENT TYPE: {event_type}')
    if event_type:
        old_data = read_data(event_type)
        write_data(old_data)

def read_data(event_type):
    
    data = None

    with Session(engine) as session:
        data = session.query(MsgCreate).order_by(
            MsgCreate.last_updated.desc()).first()
    if data is None:
        return {
            'msg_code': 'x',
            'event_num': 0,
            'msg_string': 'no message',
            'last_updated': datetime.fromtimestamp(0) # datatime.now() - timedelta(100.0)
        } 
    else:
        print(f"THIS IS DATA ITEM: {data.msg_code, data.event_num, data.msg_string}")
        if event_type == 'receiver':
            data.msg_code = '0001'
        elif event_type == 'storage':
            data.msg_code = '0002'
        elif event_type == 'processor_startup':
            data.msg_code = '0003'
        elif event_type == 'processor_more':
            data.msg_code = '0004'

        LOGGER.info(f"Received event type: {event_type}, Message Code: {data.msg_code}")
        return data.to_dict()
    

def write_data(body):
    with Session(engine) as session:
        # Check if the record with the same message code exists
        body = session.query(MsgCreate).filter(MsgCreate.msg_code == body['msg_code']).first()
        body.msg_id = str(uuid4())
        print(f"THIS IS EXISTING RECORD MSG CODE: {body.msg_code}")
        # body['msg_id'] = str(uuid4())
        # If the record exists, update the event_num column
        # existing_record.event_num += 1
        # existing_record.msg_string = f'{existing_record.msg_code} Events Logged: {existing_record.event_num}'
        body.event_num += 1
        body.msg_string = f"{body.msg_code} Events Logged: {body.event_num}"

        data = MsgCreate(
            body.msg_id,
            body.msg_code,
            body.event_num,
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