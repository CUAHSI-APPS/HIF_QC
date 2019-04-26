#connect to Redis
import uuid
from redis import Redis
redis = Redis(host='redis', port=6379)

class SessionTicketCounter():

    def __init__(self):
        #redis.set('Session Counter',str(uuid.uuid1()))
        pass


    def TakeTicket(self, fileName=""):
        #Ticket = str(redis.get('Session Counter'))
        Ticket = str(uuid.uuid1())
        redis.set(Ticket, fileName)
        return Ticket
