from models import Msg
import datetime
from datetime import datetime


class MsgCreate(Msg):

    def __init__(self, msg_id, msg_code, event_num, msg_string):
        self.msg_id = msg_id
        self.msg_code = msg_code
        self.event_num = event_num
        self.msg_string = msg_string
        self.last_updated = datetime.now()

    def to_dict(self):
        dicti = {}
        dicti['msg_id'] = self. msg_id
        dicti['msg_code'] = self.msg_code
        dicti['event_num'] = self.event_num
        dicti['msg_string'] = self.msg_string
        dicti['last_updated'] = self.last_updated

        return dicti