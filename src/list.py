import json
import os
import socket

import redis

ALLOW_CIDR = os.getenv('ALLOW_CIDR', 'x.x.x.x')
REDIS_IP = os.getenv('REDIS_IP', 'redis.url')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_QUERY_KEY = os.getenv('REDIS_QUERY_KEY', 'group:{}:key')
REDIS_QUERY_USER = os.getenv('REDIS_QUERY_USER', 'group:{}:user')


def list(event, context):
    print("connecting to host={} port={}".format(REDIS_IP, REDIS_PORT))
    queue_status = {}

    redis_connection = redis.Redis(host=REDIS_IP, port=REDIS_PORT)
    queue_keys = redis_connection.keys(REDIS_QUERY_KEY.format('*'))

    for queue_key in queue_keys:
        print('found key')
        queue_name = queue_key.decode('utf-8').split(':')[1]
        queue_uuids = redis_connection.lrange(REDIS_QUERY_KEY.format(queue_name), 0, -1)
        for uuid in queue_uuids:
            print('found user')
            uuid = uuid.decode('utf-8')
            if queue_name not in queue_status:
                queue_status[queue_name] = []
            user_host = redis_connection.get(REDIS_QUERY_USER.format(uuid)).decode('utf-8')
            user, host = user_host.split(':')
            queue_status[queue_name].append({'user': user, 'host': host})
    print('queue_status')

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True
        },
        "body": json.dumps(queue_status)
    }


if __name__ == '__main__':
    print(list('', ''))
