from connexion import FlaskApp, NoContent
import json
from load_config import load_log_conf
from database_config import load_db_conf
from pykafka import KafkaClient
from pykafka.common import OffsetType 
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware

LOGGER = load_log_conf()

KAFKA_HOST, KAFKA_PORT, KAFKA_TOPIC= load_db_conf()
client = KafkaClient(hosts=f'{KAFKA_HOST}:{KAFKA_PORT}')
topic = client.topics[str.encode(KAFKA_TOPIC)]

def get_products(index):
    hostname = "%s:%d" % (KAFKA_HOST,KAFKA_PORT)
    print(hostname)
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(KAFKA_TOPIC)]
    print("-------------------------------------------")
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    LOGGER.info(f"Retrieving get product at index: {index} ")
    
    current_index = 0

    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg["type"] == "add product create":
                if current_index == index:
                    return msg["payload"], 200
                else:
                    current_index += 1
                
    except:
        LOGGER.error("No more messages found")
        
    LOGGER.error("Could not find get product at index %d" % index)
    return { "message": "Not Found"}, 404

def get_reviews(index):
    """ Process event messages """
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    LOGGER.info(f"Retrieving get review at index: {index} ")
    
    current_index = 0

    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            print(msg)
            if msg["type"] == "add product review":
                if current_index == index:
                    return msg["payload"], 200
                else:
                    current_index += 1
            
    except:
        LOGGER.error("No more messages found")
        
    LOGGER.error("Could not find get review at index %d" % index)
    return { "message": "Not Found"}, 404


app = FlaskApp(__name__, specification_dir='')
app.add_api("./BESTIE-commerce.yaml", strict_validation=True, validate_responses=True)

# # Core:
# app = FlaskApp(__name__)

app.add_middleware(
    CORSMiddleware,
    position=MiddlewarePosition.BEFORE_EXCEPTION,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8110)
    print("audit service closed...")