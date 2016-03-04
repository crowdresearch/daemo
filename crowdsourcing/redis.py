from ws4redis.publisher import redis_connection_pool, StrictRedis


class RedisProvider(object):

    def __init__(self, **kwargs):
        self._connection = StrictRedis(connection_pool=redis_connection_pool)

    def set(self, key, value, expire=None):
        return self._connection.set(name=key, value=value)

    def get(self, key):
        return self._connection.get(name=key)

    def push(self, key, values):
        return self._connection.lpush(key, values)

    def exists(self, key):
        return self._connection.exists(name=key)

    def get_list(self, key):
        return self._connection.lrange(name=key, start=0, end=-1)

    def set_scan(self, key, match=None):
        return self._connection.sscan_iter(name=key, match=match)

    def set_add(self, key, values):
        return self._connection.sadd(key, values)

    @staticmethod
    def build_key(prefix, key):
        return str(prefix) + ':' + str(key)
