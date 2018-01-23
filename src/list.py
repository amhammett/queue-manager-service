import os
import socket

import redis

ALLOW_CIDR = os.getenv('ALLOW_CIDR', 'x.x.x.x')
REDIS_HOST = os.getenv('REDIS_HOST', 'redis.url')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_QUERY_KEY = os.getenv('REDIS_QUERY_KEY', 'group:{}:key')
REDIS_QUERY_USER = os.getenv('REDIS_QUERY_USER', 'group:{}:user')


def redis_connectable():
    connectable = False

    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    s.settimeout(1)

    try:
        if s.connect_ex((REDIS_HOST, REDIS_PORT)) == 0:
            connectable = True
    except socket.gaierror:
        print("can't resolve hostname")

    return connectable


def list(event, context):
    print("connecting to host={} port={}".format(REDIS_HOST, REDIS_PORT))
    queue_status = {}

    if(redis_connectable()):
        redis_connection = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
        queue_keys = redis_connection.keys(REDIS_QUERY_KEY.format('*'))

        for queue_key in queue_keys:
            queue_name = queue_key.decode('utf-8').split(':')[1]
            queue_uuids = redis_connection.lrange(REDIS_QUERY_KEY.format(queue_name), 0, -1)
            for uuid in queue_uuids:
                uuid = uuid.decode('utf-8')
                if queue_name not in queue_status:
                    queue_status[queue_name] = []
                user_host = redis_connection.get(REDIS_QUERY_USER.format(uuid)).decode('utf-8')
                user, host = user_host.split(':')
                queue_status[queue_name].append({'user': user, 'host': host})

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True
        },
        "body": queue_status
    }


if __name__ == '__main__':
    print(list('', ''))
