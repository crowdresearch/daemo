from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage


class SocketManager:
    def __init__(self):
        pass

    def publish(self, publisher, message):
        redis_message = RedisMessage(message)
        publisher.publish_message(redis_message)

    def broadcast(self, channel, message):
        publisher = RedisPublisher(facility=channel, broadcast=True)
        self.publish(publisher, message)

    def broadcast_users(self, channel, message, users):
        publisher = RedisPublisher(facility=channel, users=users)
        self.publish(publisher, message)

    def broadcast_groups(self, channel, message, groups):
        publisher = RedisPublisher(facility=channel, groups=groups)
        self.publish(publisher, message)

    def broadcast_sessions(self, channel, message, sessions):
        publisher = RedisPublisher(facility=channel, sessions=sessions)
        self.publish(publisher, message)
