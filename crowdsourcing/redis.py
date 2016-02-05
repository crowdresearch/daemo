from ws4redis.publisher import redis_connection_pool, StrictRedis


class RedisProvider(object):

    def __init__(self, **kwargs):
        self._connection = StrictRedis(connection_pool=redis_connection_pool)

    def set(self, key, value, expire=None):
        self._connection.set(name=key, value=value)
        return "OK"

    def get(self, key):
        return self._connection.get(name=key)

    def push(self, key, values):
        self._connection.lpush(name=key, *values)
        return "OK"

    def exists(self, key):
        return self._connection.exists(name=key)

    def get_list(self, key):
        return self._connection.lrange(name=key, start=0, end=-1)

    @staticmethod
    def build_key(prefix, key):
        return str(prefix) + ':' + str(key)
