import connexion
from connexion import NoContent
from load_config import load_app_conf, load_log_conf
import time
from pykafka import KafkaClient
import datetime
import json
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware

# Define configration settings by configuration file: -------------------------
LOGGER = load_log_conf()
EVENTSTORE, EVENT, RETRY = load_app_conf()

# Define global variables: ----------------------------------------------------
KAFKA_HOST = EVENT["hostname"]
KAFKA_HOST_PORT = EVENT["port"]
KAFKA_TOPIC = EVENT["topic"]

MAX_RETRIES = RETRY["max_retry"]
RETRY_DELAY_SECONDS = RETRY["delay_seconds"]

# Kafka Setup: ----------------------------------------------------------------
def retry_logic():
    '''
    TODO: This function attempts to establish a connection with Kafka by creating a Kafka client with the specified host 
    and port. It retries the connection according to the specified maximum number of retries and delay between retries. If 
    the connection is successful, it returns a Kafka producer.
    (Kafka server as a receiver receives data and sends it to database)
    '''
    current_retry = 0

    while current_retry < MAX_RETRIES:
        try:
            client = KafkaClient(hosts=f'{KAFKA_HOST}:{KAFKA_HOST_PORT}')
            topic = client.topics[str.encode(KAFKA_TOPIC)]
            producer =  topic.get_sync_producer()
            LOGGER.info("Connected to Kafka")
            return producer
        except Exception as e:
            LOGGER.error(f"Failed to connect to Kafka (retry {current_retry + 1}/{MAX_RETRIES}): {e}")
            time.sleep(RETRY_DELAY_SECONDS)
            current_retry += 1

    if current_retry == MAX_RETRIES:
        LOGGER.error("Max retries reached. Exiting.")

        
producer = retry_logic()
LOGGER.info(f'Producer: {producer}')

# Events Handling Functions: ----------------------------------------------------------------
def add_new_product(body):
    '''
    TODO: This is an event function to create a request when there is new product
    '''

    try:
        headers = {"Content-Type": "application/json"}
        trace_id = str(time.time_ns())
        
        LOGGER.info(f"Received event 'product_create' request with a trace id of {trace_id}")
        body["trace_id"] = trace_id

        
        msg = { "type": "add product create",
                "datetime" :datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "payload": body
            }
        msg_str = json.dumps(msg)
        producer.produce(msg_str.encode('utf-8'))
    except Exception as e:
        return str(e), 501

    return NoContent, 201

def add_product_review(body):
    '''
    TODO: This is an event function to create a request when there is new review
    '''


    try:
        headers = {"Content-Type": "application/json"}
        trace_id = str(time.time_ns())
        
        LOGGER.info(f"Received event 'product_review' request with a trace id of {trace_id}")
        body["trace_id"] = trace_id
        
        msg = { "type": "add product review",
                "datetime" :datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "payload": body
            }
        msg_str = json.dumps(msg)
        producer.produce(msg_str.encode('utf-8'))
    except Exception as e:
        return str(e), 501

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
    app.run(host="0.0.0.0",port=8080)
