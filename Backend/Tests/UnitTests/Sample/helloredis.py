import redis 
redis_host = "localhost"
redis_port = 6379
redis_password = ""
def foo(value):
    r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password)
    r.set('a',value)
    return r.get('a')


