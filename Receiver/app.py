import connexion
from connexion import NoContent
import requests
import config_setting
import time
from pykafka import KafkaClient
import datetime
import json
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware

LOGGER = config_setting.logger

MAX_RETRIES = config_setting.app_config["retry_logs"]["max_retries"]
RETRY_DELAY_SECONDS = config_setting.app_config["retry_logs"]["delay_seconds"]
CURRENT_RETRY = config_setting.app_config["retry_logs"]["current_retry"]

def retry_logic():
    host = config_setting.app_config["events"]["hostname"]
    port = config_setting.app_config["events"]["port"]

    while CURRENT_RETRY < MAX_RETRIES:
        try:
            client = KafkaClient(hosts=f'{host}:{port}')
            topic = client.topics[str.encode(config_setting.app_config["events"]["topic"])]
            producer =  topic.get_sync_producer()
            LOGGER.info("Connected to Kafka")
            return producer
        except Exception as e:
            LOGGER.error(f"Failed to connect to Kafka (retry {CURRENT_RETRY+ 1}/{MAX_RETRIES}): {e}")
            time.sleep(RETRY_DELAY_SECONDS)
            CURRENT_RETRY += 1

    if CURRENT_RETRY == MAX_RETRIES:
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

    return NoContent, 201

def add_product_review(body):
    
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
