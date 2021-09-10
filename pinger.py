import time
import requests

second = 1
minute = 5 * second

while 1:
    requests.get('localhost:8080/update/')
    time.sleep(5 * minute)
