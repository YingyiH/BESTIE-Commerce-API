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

HOST = config_setting.app_config["events"]["hostname"]
PORT = config_setting.app_config["events"]["port"]
CLIENT = KafkaClient(hosts=f'{HOST}:{PORT}')
TOPIC= CLIENT.topics[str.encode(config_setting.app_config["events"]["topic"])]


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
            "datetime" :datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
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
            "datetime" :datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
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
