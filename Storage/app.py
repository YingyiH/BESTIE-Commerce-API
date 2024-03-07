from datetime import datetime
from operator import and_
import connexion
from connexion import NoContent
from sqlalchemy.orm import Session
from models import Base
from product_create import ProductCreate
from product_review import CommentCreate
from create_table_mysql import create_database, engine
from load_config import load_log_conf
from database_config import load_db_conf
from pykafka import KafkaClient
import datetime
import json
from pykafka.common import OffsetType 
from threading import Thread

LOGGER = load_log_conf()

USER, PASSWORD, HOST, PORT, DB, KAFKA_HOST, KAFKA_PORT, KAFKA_TOPIC= load_db_conf()

def process_messages():
    """ Process event messages """
    hostname = "%s:%d" % (KAFKA_HOST,KAFKA_PORT)
    print(hostname)
    print("-------------------------------------------")
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(KAFKA_TOPIC)]
    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group', reset_offset_on_start=False, auto_offset_reset=OffsetType.LATEST)

    # This is blocking - it will wait for a new message
    for msg in consumer:
        
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        LOGGER.info("Message: %s" % msg)
        payload = msg["payload"]
        if msg["type"] == "add product create": # Change this to your event type
        # Store the event1 (i.e., the payload) to the DB
            add_new_product(payload)
            print(f'test')
            LOGGER.info("Added new product")
        elif msg["type"] == "add product review": # Change this to your event type
        # Store the event2 (i.e., the payload) to the DB
            add_product_review(payload)
            LOGGER.info("Added product review")
        # Commit the new message as being read
        consumer.commit_offsets()

def get_products(start_timestamp, end_timestamp):
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

def add_new_product(body):

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


    LOGGER.debug(
        f'Stored event "product create" request with a trace id of {trace_id}')
    
    LOGGER.info(f"Connecting to DB. Hostname: {HOST}, Port:{PORT}")
    
    return NoContent, 201


def add_product_review(body):

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

    LOGGER.debug(
        f'Stored event "review create" request with a trace id of {trace_id}')
    
    LOGGER.info(f"Connecting to DB. Hostname: {HOST}, Port:{PORT}")
    
    return NoContent, 201

# use the openapi in the Receiver Service:
app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("BESTIE-commerce.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    create_database()
    t1 = Thread(target=process_messages)
    t1.daemon = True
    t1.start()
    app.run(port=8090)
