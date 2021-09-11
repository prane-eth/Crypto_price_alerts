import time
import requests

second = 1
minute = 5 * second

print('Started subprocess pinger.py')

while 1:
    # Load /update/ every 5 minutes
    requests.get('http://localhost:8080/update/')
    time.sleep(5 * minute)
