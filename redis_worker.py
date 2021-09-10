import os

import redis
from rq import Worker, Queue, Connection

listen = ['default']

redis_url = 'redis://:BJqBC9awpkqSOoJGohUNCLTtxoBQLVwY@redis-11039.c54.ap-northeast-1-2.ec2.cloud.redislabs.com:11039/myredis'
conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()