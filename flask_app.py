
import os
import time
import subprocess
import hashlib
from flask import Flask, request, render_template_string
import pandas as pd
# from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from send_email import send_email

# postgres database is hosted on Heroku
DB_URL = 'postgresql://miznhxqqdtwulp:9e61606a7a31c2e26ca389f5e76aa33ffd16e342f6d606e9f6874669f368e470' \
       + '@ec2-44-196-146-152.compute-1.amazonaws.com:5432/d65rebcms2v45r'

app = Flask(__name__)
app.secret_key = 'my_secret_key_1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL  # 'postgresql:///MyDB.db'
db = SQLAlchemy(app)

from rq import Queue
from redis_worker import conn  # local file
q = Queue(connection=conn, default_timeout = 7200)

subprocess.call(['python3', 'pinger.py'])
subprocess.call(['python3', 'redis_worker.py'])


class var:  # a class to store variables
    PRICES_URL = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD' \
               + '&order=market_cap_desc&per_page=100&page=1&sparkline=false'
    prices_df = pd.read_json(PRICES_URL)
    available_coins = prices_df.symbol.tolist()
    token_email = pd.DataFrame.from_dict({
        'access_token': ['9812648932al'],
        'email': ['abc@gmail.com']
    })
    alerts = pd.DataFrame(columns=['email', 'currency', 'target_price', 'targeted_for'])
    alert_history = pd.DataFrame(columns=['email', 'currency', 'target_price', 'status'])
    db_engine = None  # Initialize later
    #
    def get_email(access_token=''):
        df = var.token_email
        indexes = df[df['access_token'] == access_token].index.to_list()
        if indexes:  # if email is found in the dataframe
            return df.iloc[indexes[0]].email
        else:
            return ''
    #
    def update_database():
        var.alerts.to_sql('alerts', con=db.engine, index=False, if_exists='replace')
        var.alert_history.to_sql('alert_history', con=db.engine, index=False, if_exists='replace')
        var.token_email.to_sql('token_email', con=db.engine, index=False, if_exists='replace')
        print('Updated database')
    #
    def send_alert(email, currency, target_price, new_price):
        print('sending alert')
        var.alert_history.loc[len(var.alert_history)] = \
                [email, currency, target_price, 'triggered']  # add to alert history
        var.update_database()
        subject = 'Alert! Change in price for ' + currency
        message = 'Dear user, \n You have set an alert for {currency} ' \
                + 'for {target_price}. <br> <b> Price is now {current_price} </b>' \
                .format(currency=currency, target_price=target_price, new_price=new_price)
        # Send to queue
        job = q.enqueue_call(
            func=send_email, args=(email, subject, message,),
            result_ttl=5000
        )
        print(job.get_id())


# load old data
try:
    var.alerts = pd.read_sql_table('alerts', db.engine,
            columns=['email', 'currency', 'target_price', 'targeted_for'])
    var.alert_history = pd.read_sql_table('alert_history', db.engine,
            columns=['email', 'currency', 'target_price', 'status'])
    var.token_email = pd.read_sql_table('token_email', db.engine,
            columns=['access_token', 'email'])
    # print(var.token_email)
    print('loaded old data from DB to dataframe')
except Exception:
    print('Error reading database')


@app.route('/update/')
def update():
    ' Check new prices and notify users '
    # /update/ url will be called by a background process at regular intervals of time
    var.prices_df = pd.read_json(var.PRICES_URL)  # get new prices
    df = var.prices_df  # current prices
    notified_count = 0
    for row in var.alerts:
        print(row)
        email = row[0]
        currency = row[1]
        target_price = row[2]
        targeted_for = row[3]
        new_price = df.loc[df.symbol == currency]
        new_price = new_price.current_price.values[0]
        #
        if new_price == target_price:
            # alert for reaching target price
            var.send_alert(email, currency, target_price, new_price)
            notified_count += 1
        elif targeted_for == 'increase' and new_price > target_price:
            # alert for increasing
            var.send_alert(email, currency, target_price, new_price)
            notified_count += 1
        elif targeted_for == 'decrease' and new_price < target_price:
            # targeted for decreasing
            var.send_alert(email, currency, target_price, new_price)
            notified_count += 1
    #
    return 'Notified: ' + str(notified_count)


@app.route('/alerts/create/')
def create():
    ' create alert in dataframe '
    access_token = request.args.get('access_token')
    currency = request.args.get('currency')
    target_price = request.args.get('target_price')
    email = var.get_email(access_token)
    if not email:
        return 'Email not found'
    if currency not in var.available_coins:
        return 'Currency not available'
    # add alert to dataframe
    df = var.prices_df  # current prices
    current_price = df.loc[df.symbol == currency]
    current_price = current_price.current_price.values[0]
    targeted_for = ''
    if int(target_price) > int(current_price):
        targeted_for = 'increase'
    else:
        targeted_for = 'decrease'
    var.alerts.loc[len(var.alerts)] = [email, currency, target_price, targeted_for]
    var.alert_history.loc[len(var.alert_history)] = [email, currency, target_price, 'created']
    var.update_database()
    return "Alert created"


@app.route('/alerts/delete/')
def delete():
    ' delete alert from dataframe '
    access_token = request.args.get('access_token')
    currency = request.args.get('currency')
    target_price = request.args.get('target_price')
    email = var.get_email(access_token)
    if not email:
        return 'Email not found'
    df = var.alerts
    df.drop(df.loc[  # drop the row which matches the values
                (df.email == email) & (df.currency == currency)
                & (df.target_price == target_price)
            ].index, inplace=True)
    var.alert_history.loc[len(var.alert_history)] = [email, currency, target_price, 'deleted']
    # df.reset_index()
    var.update_database()
    return "Alert deleted"


@app.route('/alerts/fetch/')
def fetch():
    ' fetch all alert history '
    access_token = request.args.get('access_token')
    email = var.get_email(access_token)
    if not email:
        return 'Email not found'
    df = var.alert_history
    df = df.loc[df.email == email]
    html_code = df.to_html(index=False)
    return render_template_string(html_code)


@app.route('/signup/')
def signup():
    ' signup with email to get access token '
    email = request.args.get('email')
    if not email:
        email = 'abc@abc.com'
        # return 'visit /signup/?email=user12@gmail.com to signup'
    timestamp = str(time.time())
    access_token = email + timestamp
    access_token = access_token.encode('utf-8')
    access_token = hashlib.md5(bytes(access_token))
    access_token = access_token.hexdigest()
    var.token_email.loc[len(var.token_email.index)] = [access_token, email]
    # print(var.token_email)
    return 'access_token=' + access_token


@app.route('/coins/')
def coins():
    html_code = pd.DataFrame(var.prices_df.symbol).to_html(index=False)
    return render_template_string(html_code)


@app.route('/prices/')
def prices():
    html_code = var.prices_df.to_html(index=False)
    return render_template_string(html_code)


if __name__ == "__main__":
    try:
        app.run(port=8080, debug=True)
    except KeyboardInterrupt:
        print('got a KeyboardInterrupt')  # after program ends
        os.system('killall -9 python3')  # kill all started subprocesses

