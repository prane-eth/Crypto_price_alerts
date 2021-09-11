# Krypto_task

## How to run the project:

To install the requirements:

`python3 -m pip install -r requirements.txt`

To run the code:

`python3 flask_app.py`

It will automatically start the other processes which are required

Note: API calls may be slow because of sending data to database. To increase the speed, kindly remove the lines which store data in DB.


## Endpoints

`/alerts/create/` creates alert \
`/alerts/delete/` deletes an alert \
`/alerts/fetch/` fetches the alert history \
`/signup/` to signup with email \
`/update/` to check the new prices and send the alert to the users. This is made to be called by `pinger.py` \
`/coins/` to get list of coins \
`/prices/` to get prices and details of all the coins


## API usage

After http://127.0.0.1:8080/, add the following

`/signup/?email=abc@abc.com` to signup with email

`/alerts/create/?currency=btc&target_price=1000&access_token=<access-token>` to create alert with BTC at target price of 1000

`/alerts/delete/?currency=btc&target_price=1000&access_token=<access-token>` to create alert with BTC which has been set with a target price of delete

`/alerts/fetch/?access_token=<access-token> `to fetch alerts. It returns a HTML page with the history of `create, delete, trigger`

`/coins/` to get list of coins

`/prices/` to get prices and details of all the coins

`/update/` to check the new prices and send the alert to the users. This is made to be called by `pinger.py`


## My approach
In the Python Flask app code, I created a class named `var` to store the variables. \
I used Redis Online and Heroku's Postgresql for hosting them online. \
The code creates a subprocess which starts Redis worker and a pinger to run in parallel.\
Pinger loads /update/ of Flask app every 5 minutes. Flask app will then fetch the new prices of all the coins and sends alert to the users' email address.\
The file send_email.py contains the code required to send an email.

All the tables are stored in Pandas DataFrame. When any dataframe is updated, database will be updated immediately. \
When program starts, it restores the old data from the database.

When there is an alert to be sent to the user, it is added to the Redis queue. Then `redis_worker.py` sends an email to the user.



### Note
I was not informed about the extension of deadline till 10 AM. I couldn't improve the code. \
If you want to allow me to improve code or if you want any improvements, kindly send an email.