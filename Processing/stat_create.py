from models import Stat
import datetime
from datetime import datetime


class StatCreate(Stat):

    def __init__(self, reading_id, num_products, num_reviews, num_onsale_products, max_price):
        self.reading_id = reading_id
        self.num_products = num_products
        self.num_reviews = num_reviews
        self.num_onsale_products = num_onsale_products
        self.max_price = max_price
        self.last_updated = datetime.now()

    def to_dict(self):
        dict = {}
        dict['reading_id'] = self.reading_id
        dict['num_products'] = self.num_products
        dict['num_reviews'] = self.num_reviews
        dict['num_onsale_products'] = self.num_onsale_products
        dict['max_price'] = self.max_price
        dict['last_updated'] = self.last_updated

        return dict