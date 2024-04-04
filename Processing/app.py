import requests
from connexion import FlaskApp
from load_config import load_log_conf, load_app_conf
from sqlalchemy.orm import Session
from create_datebase import engine, create_database
from stat_create import StatCreate
from datetime import datetime, timedelta
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from data_process import product_processing, review_processing
from models import Stat
from uuid import uuid4
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware

# Define configration settings by configuration file: -------------------------
LOGGER, LOG_CONFIG_FILE = load_log_conf()
SECONDS, EVENT_URL, APP_CONFIG_FILE = load_app_conf()

LOGGER.info("App Conf File: %s" % APP_CONFIG_FILE )
LOGGER.info("Log Conf File: %s" % LOG_CONFIG_FILE)

# Populating Statistics: ------------------------------------------------------
def populate_stats():
    # try:
    print("BEFORE")
    data = processing()
    print("AFTER DATA")
    write_data(data)

    # except Exception as e:
    #     LOGGER.debug("Error processing")
        # LOGGER.error(str(e))

# Initializing Scheduler: -----------------------------------------------------
def init_scheduler():
    
    populate_stats_variables = populate_stats

    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats_variables, 'interval', seconds= SECONDS)
    sched.start()

    # return sched, app_config, EVENT_URL
    return sched, EVENT_URL

SCHEDULED, EVENT_URL = init_scheduler()


# Read Statistics Data: -----------------------------------------------------------------
def read_data():
    data = None

    with Session(engine) as session:
        data = session.query(StatCreate).order_by(
            StatCreate.last_updated.desc()).first()
        
    if data is None:
        return {
            'num_products': 0, 
            'num_reviews': 0, 
            'num_onsale_products': 0, 
            'max_price': 0, 
            'last_updated': datetime.fromtimestamp(0) # datatime.now() - timedelta(100.0)
        }
    else:
        return data.to_dict()
    
# Write Statistics Data: ----------------------------------------------------------------
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

# Endpoint to Get Statistics: ------------------------------------------------------------
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

# Processing Events: ----------------------------------------------------------------------
def processing():

    old_data = read_data()
    time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    timestamp_dict = {
        'start_timestamp': old_data['last_updated'].strftime("%Y-%m-%dT%H:%M:%S"),
        'end_timestamp': time
    }

    product_event = requests.get(f'{EVENT_URL}/products', params=timestamp_dict, timeout=10)
    review_event = requests.get(f'{EVENT_URL}/reviews', params=timestamp_dict, timeout=10)

    product_data = product_event.json()
    review_data = review_event.json()

    LOGGER.info(f'Received {len(product_data)} products and {len(review_data)} reviews.')
    
    # updates data inplace
    product_processing(product_data, old_data)
    review_processing(review_data, old_data)
    LOGGER.info("Finished processing")

    LOGGER.debug(f'Updated statistic values: {old_data}')

    return old_data

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

app.add_api("./openai.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    print("NOT YET CREATED DATABASE--------------------------------")
    # create database
    create_database()
    print("CREATED DATABASE--------------------------------")
    # run our standalone gevent server
    init_scheduler()
    app.run(host="0.0.0.0" ,port=8100) #nosec