import connexion
from connexion import NoContent
import requests
from config_setting import load_app_conf, load_log_conf
import time
from pykafka import KafkaClient
import datetime
import json
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware

LOGGER = load_log_conf()
EVENTSTORE, EVENT, RETRY = load_app_conf()

HOST = EVENT["hostname"]
PORT = EVENT["port"]
TOPIC = EVENT["topic"]

MAX_RETRIES = RETRY["max_retry"]
RETRY_DELAY_SECONDS = RETRY["delay_seconds"]

def retry_logic():

    current_retry = 0

    while current_retry < MAX_RETRIES:
        try:
            client = KafkaClient(hosts=f'{HOST}:{PORT}')
            topic = client.topics[str.encode(TOPIC)]
            producer =  topic.get_sync_producer()
            LOGGER.info("Connected to Kafka")
            return producer
        except Exception as e:
            LOGGER.error(f"Failed to connect to Kafka (retry {current_retry + 1}/{MAX_RETRIES}): {e}")
            time.sleep(RETRY_DELAY_SECONDS)
            current_retry += 1

    if current_retry == MAX_RETRIES:
        LOGGER.error("Max retries reached. Exiting.")
        return
        
producer = retry_logic()

def get_sync_producer():

    msg_str = producer.value.decode('utf-8')
    msg = json.loads(msg_str)
    LOGGER.info("Message: %s" % msg)
    payload = msg["payload"]

    if not producer:
        LOGGER.error("Producer not available. Event not produced.")
        return
    
    if msg["type"] == "add product create":
        add_new_product(payload)
        LOGGER.info("Added new product")
    elif msg["type"] == "add product review":
        add_product_review(payload)
        LOGGER.info("Added product review")
    producer.commit_offsets()

def cleanup_producer(producer):
    try:
        producer.stop()
    except Exception as e:
        LOGGER.error(f"Error occurred during producer cleanup: {e}")

# Events
def add_new_product(body):

    try:
        headers = {"Content-Type": "application/json"}
        trace_id = str(time.time_ns())
        
        LOGGER.info(f"Received event 'product_create' request with a trace id of {trace_id}")
        body["trace_id"] = trace_id

        
        producer = TOPIC.get_sync_producer()
        msg = { "type": "add product create",
                "datetime" :datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "payload": body
            }
        msg_str = json.dumps(msg)
        producer.produce(msg_str.encode('utf-8'))

        cleanup_producer(producer)  # Call cleanup method
    except Exception as e:
        return str(e), 401

    return NoContent, 201

def add_product_review(body):
    
    try:
        headers = {"Content-Type": "application/json"}
        trace_id = str(time.time_ns())
        
        LOGGER.info(f"Received event 'product_review' request with a trace id of {trace_id}")
        body["trace_id"] = trace_id
        
        producer = TOPIC.get_sync_producer()
        msg = { "type": "add product review",
                "datetime" :datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "payload": body
            }
        msg_str = json.dumps(msg)
        producer.produce(msg_str.encode('utf-8'))

        cleanup_producer(producer)  # Call cleanup method
    except Exception as e:
        return str(e), 501

    return NoContent, 201


# use the openapi in the Receiver Service:
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
