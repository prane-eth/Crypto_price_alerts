# Crypto_price_alerts

## How to run the project:

To clone the repository: \
`git clone https://github.com/vh-praneeth/Crypto_price_alerts` \
`cd Krypto_task` to go to that directory

To install the requirements: \
`python3 -m pip install -r requirements.txt`

Before running the code: \
execute `python3 redis_worker.py` in a new terminal and minimize the terminal \
do the same with `python3 pinger.py`

To run the code: \
`python3 flask_app.py`

To test it, visit http://127.0.0.1:8080/prices/ 

Note: API calls may be slow because of sending data to the database. To increase the speed, kindly remove the lines which store data in DB. \
Flask app start may be slow due to restoration of tables from the database. \
I didn't add any code after the deadline. It is showing a commit, but it is empty.


## API Endpoints

`/alerts/create/` creates alert \
`/alerts/delete/` deletes an alert \
`/alerts/fetch/` fetches the alert history \
`/signup/` to signup with email \
`/update/` to check the new prices and send the alert to the users. This is created to be called by `pinger.py` \
`/coins/` to get the list of coins \
`/prices/` to get prices and details of all the coins


## API usage

In the URL after http://127.0.0.1:8080, add the following

`/signup/?email=abc@abc.com` to signup with email

`/alerts/create/?currency=btc&target_price=1000&access_token=<access-token>` to create alert with BTC at target price of 1000

`/alerts/delete/?currency=btc&target_price=1000&access_token=<access-token>` to create alert with BTC which has been set with a target price of delete

`/alerts/fetch/?access_token=<access-token> `to fetch alerts. It returns a HTML page with the history of `create, delete, trigger`

`/coins/` to get the list of coins

`/prices/` to get prices and details of all the coins

`/update/` to check the new prices and send the alert to the users. This is made to be called by `pinger.py`. Sometimes it is not working.


## My approach
In the Python Flask app code, I created a class named `var` to store the variables. \
Pinger loads `localhost:8080/update/` of Flask app every 5 minutes. Flask app will then fetch the new prices of all the coins and sends the alerts to the users.

When there is an alert to be sent to the user, it is added to the Redis queue. Then `redis_worker.py` receives the task and sends an email to the user.

All the tables are stored in Pandas DataFrames. When any dataframe is updated, the database will be updated immediately from the dataframe. It takes more time. \
When the program starts, it restores the old data from the database. It takes more time.

At any request, we find the email address using the access token.

Access token is md5 hash of (emailID + timestamp). Timestamp is taken at the time of creation.

### How the code notifies using active alerts:
When an alert is created, it compares the target price with the current price. It will decide whether the user wants to be notified about an increase or decrease in the price.

For each active alert entry, it checks the current prices of the given currency.

If the new price is the same as the target price, the user gets notified.
If the user has targeted for an increase and the new price is greater than the target price, the user gets notified.
Or if the user has targeted for a decrease and the new price is less than the target price, the user gets notified.


### Note
I was not informed about the extension of the deadline till 10 AM. I couldn't improve the code. If you want any improvements in the code, kindly send an email. I gained experience during my internship with Python, Flask, and APIs.

My details:  \
Email: haripraneethv@gmail.com \
College ID: 18BCE7147

## Screenshots
### Signup
![Signup](./screenshots/1_signup.png)
### Create
![Create](./screenshots/2_create.png)
### Delete
![Delete](./screenshots/3_delete.png)
### Fetch
![Fetch](./screenshots/4_fetch.png)
### Coins
![Coins](./screenshots/5_coins.png)
### Prices
![Prices](./screenshots/6_prices.png)
