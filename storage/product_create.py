from models import Product
import datetime

class ProductCreate(Product):
    def __init__(self, product_id, seller, price, onsale, description, trace_id):
        self.product_id = product_id
        self.seller = seller
        self.price = price
        self.onsale = onsale
        self.description = description
        self.date_created = datetime.datetime.now()
        self.trace_id = trace_id
        

    def to_dict(self):
        dict = {}
        dict['product_id'] = self.product_id
        dict['seller'] = self.seller
        dict['price'] = self.price
        dict['onsale'] = self.onsale
        dict['description'] = self.description
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id

        return dict