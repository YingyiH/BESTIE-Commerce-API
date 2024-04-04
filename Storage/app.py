from datetime import datetime
from operator import and_
import time
import connexion
from connexion import NoContent
from sqlalchemy.orm import Session
from models import Base
from product_create import ProductCreate
from product_review import CommentCreate
from create_table_mysql import create_database, engine
from load_config import load_log_conf, load_app_conf
from pykafka import KafkaClient
import json
from pykafka.common import OffsetType 
from threading import Thread
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware

# Define configration settings by configuration file: -------------------------
LOGGER, LOG_CONFIG_FILE = load_log_conf()
DATA, EVENT, RETRY, APP_CONFIG_FILE  = load_app_conf()

# Define global variables: ----------------------------------------------------
# DATABASE VARIABLES
USER = DATA['user']
PASSWORD = DATA['password']
HOST = DATA['hostname']
PORT = DATA['port']
DB = DATA['db']
# KAFKA HOST VARIABLES
KAFKA_HOST = EVENT['hostname']
KAFKA_HOST_PORT = EVENT['port']
KAFKA_TOPIC = EVENT['topic']
# KAFKA RETRY VARIABLES
MAX_RETRIES = RETRY['max_retry']
RETRY_DELAY_SECONDS = RETRY['delay_seconds']

LOGGER.info("App Conf File: %s" % APP_CONFIG_FILE )
LOGGER.info("Log Conf File: %s" % LOG_CONFIG_FILE)

# ----------------------------------------------------------------
def process_messages():
    '''
    TODO: This is a function to process Kafka messages
          (Kafka server as a receiver receives data and sends it to database)
    '''

    hostname = "%s:%d" % (KAFKA_HOST,KAFKA_HOST_PORT)

    # Output hostname
    print(f'Ouput: \n  hostname: {hostname}')
    print("-------------------------------------------")

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
    
    consumer = topic.get_simple_consumer(consumer_group='event_group', reset_offset_on_start=False, auto_offset_reset=OffsetType.LATEST)

    # This is blocking - it will wait for a new message
    for msg in consumer:
        
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        LOGGER.info("Message: %s" % msg)
        payload = msg["payload"]
        if msg["type"] == "add product create":
            add_new_product(payload)
            LOGGER.info("Added new product")
        elif msg["type"] == "add product review": 
            add_product_review(payload)
            LOGGER.info("Added product review")
        consumer.commit_offsets()

# Function to read request: ----------------------------------------------------------------
def get_products(start_timestamp, end_timestamp):
    '''
    TODO: This is a function to read requests of products from database
    '''

    start_timestamp_datetime = datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S")
    end_timestamp_datetime = datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S")

    data = []
    with Session(engine) as session:
        data = session.query(ProductCreate).filter(and_(
            end_timestamp_datetime > ProductCreate.date_created, ProductCreate.date_created >= start_timestamp_datetime)).all()
    res = [application.to_dict() for application in data]

    LOGGER.info("Query for applications after %s returns %d results" %
                (start_timestamp, len(res)))
    return res, 200

def get_reviews(start_timestamp, end_timestamp):
    '''
    TODO: This is a function to read requests of reviews from database
    '''
        
    start_timestamp_datetime = datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S")
    end_timestamp_datetime = datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S")

    data = []
    with Session(engine) as session:
        data = session.query(CommentCreate).filter(and_(
            end_timestamp_datetime > CommentCreate.date_created, CommentCreate.date_created >= start_timestamp_datetime)).all()

    res = [application.to_dict() for application in data]

    LOGGER.info("Query for applications after %s returns %d results" %
                (start_timestamp, len(res)))

    return res, 200

# Events Handling Functions: ----------------------------------------------------------------
def add_new_product(body):
    '''
    TODO: This is an event function to store a request when there is new product sent to Kafka server
    '''

    trace_id = body['trace_id']
    pc = ProductCreate(body['product_id'],
                       body['seller'],
                       body['price'],
                       body['onsale'],
                       body['description'],
                       body['trace_id'])

    with Session(engine) as session:
        session.add(pc)
        session.commit()


    LOGGER.debug(f'Stored event "product create" request with a trace id of {trace_id}')
    LOGGER.info(f"Connecting to DB. Hostname: {HOST}, Port:{PORT}")
    
    return NoContent, 201


def add_product_review(body):
    '''
    TODO: This is an event function to store a request when there is new review sent to Kafka server
    '''

    trace_id = body['trace_id']
    cc = CommentCreate(body['review_id'],
                       body['customer'],
                       body['location'],
                       body['rating'],
                       body['comment'],
                       body['product_id'],
                       body['trace_id'])
    
    with Session(engine) as session:
        session.add(cc)
        session.commit()

    LOGGER.debug(f'Stored event "review create" request with a trace id of {trace_id}')
    LOGGER.info(f"Connecting to DB. Hostname: {HOST}, Port:{PORT}")
    
    return NoContent, 201

# App Core Setup: ----------------------------------------------------------------
app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("BESTIE-commerce.yaml", strict_validation=True, validate_responses=True)

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
    app.run(host="0.0.0.0",port=8090) #nosec
