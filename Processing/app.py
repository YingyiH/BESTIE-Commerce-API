import requests
from connexion import FlaskApp
from load_config import load_log_conf
from sqlalchemy.orm import Session
from create_datebase import engine, create_database
from stat_create import StatCreate
from datetime import datetime, timedelta
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from data_process import product_processing, review_processing
from models import Stat
from uuid import uuid4


LOGGER = load_log_conf()

def populate_stats():
    try:
        print("BEFORE")
        data= processing()
        print("AFTER DATA")
        write_data(data)
    except Exception as e:
        LOGGER.error(str(e))

def init_scheduler():
    
    with open('conf_app.yml', 'r') as f:
        app_config = yaml.safe_load(f.read())
    
    populate_stats_variables = populate_stats

    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats_variables, 'interval', seconds= app_config['scheduler']['period_sec'])
    sched.start()
    event_url = app_config['eventstore']['url']

    return sched, app_config, event_url

SCHEDULED, _,EVENT_URL = init_scheduler()


# Read the results
def read_data():
    data = None

    with Session(engine) as session:
        data = session.query(StatCreate).order_by(
            StatCreate.last_updated.desc()).first()
        
    if data == None:
        return {
            'num_products': 0, 
            'num_reviews': 0, 
            'num_onsale_products': 0, 
            'max_price': 0, 
            'last_updated': datetime.datetime.fromtimestamp(0) # datatime.now() - timedelta(100.0)
        }
    else:
        return data.to_dict()
    
# Write the results
def write_data(body):

    with Session(engine) as session:
        print("BOOTTYY: ", body)
        body['reading_id'] = str(uuid4())
        data = StatCreate(
            body['reading_id'],
            body['num_products'],
            body['num_reviews'],
            body['num_onsale_products'],
            body['max_price']
        )

        session.add(data)
        session.commit()


def get_stats():
    # Periodically update stats readings
    
    LOGGER.info('Received product and review event request.')

    data = read_data()

    if data['num_products'] <= 0 and data['num_reviews'] <= 0:

        LOGGER.error('Empty input')
        return 'Statistics do not exist', 404
    
    LOGGER.debug(f'GET event requests returns: {data}')
    LOGGER.info('GET stats request completed')
    return data, 200

def processing():

    old_data = read_data()

    time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    timestamp_dict = {
        'start_timestamp': old_data['last_updated'].strftime("%Y-%m-%dT%H:%M:%S"),
        'end_timestamp': time
    }

    product_event = requests.get(f'{EVENT_URL}/products', params=timestamp_dict)
    review_event = requests.get(f'{EVENT_URL}/reviews', params=timestamp_dict)

    product_data = product_event.json()
    review_data = review_event.json()

    LOGGER.info(f'Received {len(product_data)} products and {len(review_data)} reviews.')
    
    # updates data inplace
    product_processing(product_data, old_data)
    review_processing(review_data, old_data)
    LOGGER.info("Finished processing")

    LOGGER.debug(f'Updated statistic values: {old_data}')

    return old_data

# Your functions here
app = FlaskApp(__name__, specification_dir='')
app.add_api("./openai.yml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    # create database
    create_database()
    # run our standalone gevent server
    init_scheduler()
    app.run(port=8100)