#connect to Redis
import uuid
from redis import Redis
redis = Redis(host='redis', port=6379)

class SessionTicketCounter():

    def __init__(self):
        Counter = redis.get('Session Counter')
        if Counter == None:
            redis.set('Session Counter',uuid.uuid1())
            Counter = 0

    def TakeTicket():
        Ticket = 'S' + redis.get('Session Counter')
