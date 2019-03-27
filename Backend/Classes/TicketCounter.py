#connect to Redis
import uuid
from redis import Redis
redis = Redis(host='redis', port=6379)

class SessionTicketCounter():

    def __init__(self):
        redis.set('Session Counter',str(uuid.uuid1()))


    def TakeTicket(self):
        Ticket = str(redis.get('Session Counter'))
        redis.set('Session Counter',str(uuid.uuid1()))
        return Ticket
