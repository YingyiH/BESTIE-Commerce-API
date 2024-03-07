from operator import and_
import connexion
from connexion import NoContent
from sqlalchemy.orm import Session
from models import Base
from product_create import ProductCreate
from product_review import CommentCreate
from create_table_mysql import create_database, engine
from load_config import load_log_conf
from datetime import datetime

LOGGER = load_log_conf()

# Get request function
def get_product_readings(start_timestamp, end_timestamp):
    print(start_timestamp, end_timestamp)
    start_timestamp = datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S")
    end_timestamp = datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S")

    messages = []

    with Session(engine) as session:
        # [ new ProductCreate({})]
        messages = session.query(ProductCreate).filter(and_(ProductCreate.date_created >= start_timestamp,ProductCreate.date_created < end_timestamp))
    
    results = [product_create.to_dict() for product_create in messages]
    LOGGER.info("Query for applications after %s returns %d results" % (start_timestamp, len(results)))

    print("GET READINGS:::: ", results)
    return results, 200


def get_reivew_readings(start_timestamp, end_timestamp):
    start_timestamp = datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S")
    end_timestamp = datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S")

    messages = []

    with Session(engine) as session:
        messages = session.query(CommentCreate).filter(and_(CommentCreate.date_created >= start_timestamp,CommentCreate.date_created < end_timestamp))
    
    results = [comment_create.to_dict() for comment_create in messages]

    LOGGER.info("Query for applications after %s returns %d results" % (start_timestamp, len(results)))
    print("GET REVIEW:::: ", results)

    return results, 200


# Post request function
def add_new_product(body):

    print("BODY: ", body)
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
    
    return NoContent, 201

# use the openapi in the Receiver Service:
app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("BESTIE-commerce.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    create_database()
    app.run(port=8090)
