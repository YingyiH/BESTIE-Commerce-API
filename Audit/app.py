from connexion import FlaskApp, NoContent
import json
from load_config import load_log_conf, load_app_conf
from pykafka import KafkaClient
from pykafka.common import OffsetType 
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware

# Define configration settings by configuration file: -------------------------
LOGGER, LOG_CONFIG_FILE = load_log_conf()
KAFKA_HOST, KAFKA_PORT, KAFKA_TOPIC, APP_CONFIG_FILE = load_app_conf()

LOGGER = LOGGER.getLogger('basicLogger')
LOGGER.info("App Conf File: %s" % APP_CONFIG_FILE )
LOGGER.info("Log Conf File: %s" % LOG_CONFIG_FILE)

CLIENT = KafkaClient(hosts=f'{KAFKA_HOST}:{KAFKA_PORT}')
TOPIC = CLIENT.topics[str.encode(KAFKA_TOPIC)]

def get_products(index):
    '''
    TODO: Read requests by index
    '''

    LOGGER.info(f"Retrieving get product at index: {index} ")
    consumer = TOPIC.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    try:
        current_index = 0
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
    return {"message": "Not Found"}, 404
    

def get_reviews(index):
    '''
    TODO: Read requests by index
    '''
    LOGGER.info(f"Retrieving get review at index: {index} ")
    consumer = TOPIC.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    
    try:
        current_index = 0
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
    return {"message": "Not Found"}, 404

# App Core Setup: ----------------------------------------------------------------
app = FlaskApp(__name__)

app.add_middleware(
    CORSMiddleware,
    position=MiddlewarePosition.BEFORE_EXCEPTION,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_api("./BESTIE-commerce.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8110) 