from models import Comment
import datetime

class CommentCreate(Comment):
    def __init__(self, review_id, customer, location, rating, comment, product_id, trace_id):
        self.review_id = review_id
        self.customer = customer
        self.location = location
        self.rating = rating
        self.comment = comment
        self.product_id = product_id
        self.date_created = datetime.datetime.now()
        self.trace_id = trace_id

    def to_dict(self):
        dict = {}
        dict['review_id'] = self.review_id
        dict['customer'] = self.customer
        dict['location'] = self.location
        dict['rating'] = self.rating
        dict['comment'] = self.comment
        dict['product_id'] = self.product_id
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id

        return dict

    