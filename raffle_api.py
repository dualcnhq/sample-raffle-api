#!/usr/bin/env python
import boto3
import datetime
import os
import uuid

from flask import Flask, jsonify, abort, request, make_response, url_for
from flask_httpauth import HTTPBasicAuth
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute
from werkzeug.security import generate_password_hash, check_password_hash
from pytz import timezone

app = Flask(__name__)
auth = HTTPBasicAuth()

# Database Model
class User(Model):
    class Meta:
        table_name = os.environ.get('STAGE', 'dev') + '.users'
        region = boto3.Session().region_name
        host = 'http://localhost:8000' \
            if not os.environ.get('LAMBDA_TASK_ROOT') else None
    id = UnicodeAttribute(hash_key=True)
    first_name = UnicodeAttribute()
    last_name = UnicodeAttribute()
    email = UnicodeAttribute()
    password = UnicodeAttribute()
    street = UnicodeAttribute()
    city = UnicodeAttribute()
    num_of_entries = NumberAttribute(default=0)
    gender = UnicodeAttribute()
    mobile_number = UnicodeAttribute()
    birthday = UnicodeAttribute()
    # accepted_terms / campaign_id that user joined to
    date_created = UTCDateTimeAttribute()
    date_updated = UTCDateTimeAttribute()
    last_login = UTCDateTimeAttribute()


class Purchase(Model):
    class Meta:
        table_name = os.environ.get('STAGE', 'dev') + '.purchases'
        region = boto3.Session().region_name
        host = 'http://localhost:8000' \
            if not os.environ.get('LAMBDA_TASK_ROOT') else None
    id = UnicodeAttribute(hash_key=True)
    user_id = UnicodeAttribute()
    amount = NumberAttribute()
    store_name = UnicodeAttribute()
    card_used = UnicodeAttribute()
    transaction_date = UnicodeAttribute()
    transaction_type = UnicodeAttribute()
    campaign_id = UnicodeAttribute()
    campaign_name = UnicodeAttribute()
    date_created = UTCDateTimeAttribute()


# Auth & Response Messages
@auth.get_password
def get_password(username):  # TODO
    if username == 'admin':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)

@app.errorhandler(404)
@app.errorhandler(Model.DoesNotExist)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

# Helper Functions
def make_user(user):
    return {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'password': user.password,
        'address': {
            'street': user.street,
            'city': user.city
        },
        'num_of_entries': user.num_of_entries,
        'gender': user.gender,
        'mobile_number': user.mobile_number,
        'birthday': user.birthday,
        'date_created': user.date_created,
        'date_updated': user.date_updated,
        'last_login': user.last_login
    }

def make_purchase(purchase):
    return {
        'id': purchase.id,
        'user_id': purchase.user_id,
        'amount': purchase.amount,
        'store_name': purchase.store_name,
        'card_used': purchase.card_used,
        'transaction_date': purchase.transaction_date,
        'transaction_type': purchase.transaction_type,
        'date_created': purchase.date_created,
        'campaign': {
            'id': purchase.campaign_id,
            'name': purchase.campaign_name
        }
    }

## Endpoints
@app.route('/', methods=['GET'])
def index():
    return jsonify(
        {
            'name': 'user',
            'version': os.environ.get('LAMBDA_VERSION', 'dev'),
            'stage': os.environ['STAGE']
        },
        {
            'name': 'purchases',
            'version': os.environ.get('LAMBDA_VERSION', 'dev'),
            'stage': os.environ['STAGE']
        }
    )

## Users Endpoint
@app.route('/login', methods=['POST', 'GET']) # TODO
def login():
    #error = None
    if request.method == 'POST':
        data = request.get_json()
        print 'username: ' + data.get('username')
        print 'password: ' + data.get('password')

        #if valid_login(request.form['username'],
        #               request.form['password']):
        #    return log_the_user_in(request.form['username'])
        #else:
        #    error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    #return error
    return "login???"


@app.route('/users', methods=['GET'])
@auth.login_required
def get_users():
    return jsonify({'users': [make_user(user) for user in User.scan()]})


@app.route('/users/<user_id>', methods=['GET'])
@auth.login_required
def get_user(user_id):
    return jsonify({'user': make_user(User.get(user_id))})


@app.route('/users', methods=['POST'])
@auth.login_required
def create_user():
    dt = datetime.datetime.now(timezone('Asia/Manila')) #.strftime("%Y-%m-%d %H:%M:%S")
    data = request.get_json()

    if data is None or 'first_name' not in data:
        abort(400)

    user = User(
        id = uuid.uuid4().hex,
        first_name = data.get('first_name', ''),
        last_name = data.get('last_name', ''),
        email = data.get('email', ''),
        password = generate_password_hash(data.get('password', '')),
        street = data.get('street', ''),
        city = data.get('city', ''),
        gender = data.get('gender', ''),
        mobile_number = data.get('mobile_number', ''),
        birthday = data.get('birthday', ''),
        date_created = dt,
        date_updated = dt,
        last_login = dt)
    user.save()
    return jsonify({'user': make_user(user)}), 201


@app.route('/users/<user_id>', methods=['PUT'])
@auth.login_required
def update_user(user_id):
    user = User.get(user_id)
    data = request.get_json()
    dt = datetime.datetime.now(timezone('Asia/Manila'))
    if not data:
        abort(400)

    user.first_name = data.get('first_name', user.first_name or '')
    user.last_name = data.get('last_name', user.last_name or '')
    user.email = data.get('email', user.email or '')
    user.password = generate_password_hash(data.get('password', user.password or ''))
    user.street = data.get('street', user.street or '')
    user.city = data.get('city', user.city or '')
    user.gender = data.get('gender', user.gender or '')
    user.mobile_number = data.get('mobile_number', user.mobile_number or '')
    user.birthday = data.get('birthday', user.birthday or '')
    user.date_updated = dt
    user.save()
    return jsonify({'user': make_user(user)})


@app.route('/users/<user_id>', methods=['DELETE'])
@auth.login_required
def delete_user(user_id):
    user = User.get(user_id)
    user.delete()
    return make_response(jsonify({'message': 'Deleted successfully'})), 204


## Purchases Endpoint
@app.route('/purchases', methods=['GET'])
@auth.login_required
def get_purchases():
    return jsonify({'purchases': [make_purchase(purchase) for purchase in Purchase.scan()]})


@app.route('/purchases/<purchase_id>', methods=['GET'])
@auth.login_required
def get_purchase(purchase_id):
    return jsonify({'purchase': make_purchase(Purchase.get(purchase_id))})


@app.route('/purchases', methods=['POST'])
@auth.login_required
def create_purchase():
    dt = datetime.datetime.now(timezone('Asia/Manila'))
    data = request.get_json()

    if data is None or 'amount' not in data:
        abort(400)
    purchase = Purchase(id = uuid.uuid4().hex,
                user_id = data.get('user_id', ''),
                amount = data.get('amount', 0),
                store_name = data.get('store_name', ''),
                card_used = data.get('card_used', ''),
                transaction_date = data.get('transaction_date', ''),
                transaction_type = data.get('transaction_type', ''),
                campaign_id = 'campaign_123',
                campaign_name = 'SM Campaign',
                date_created = dt)
    purchase.save()
    return jsonify({'purchase': make_purchase(purchase)}), 201


@app.route('/purchases/<purchase_id>', methods=['DELETE'])
@auth.login_required
def delete_purchase(purchase_id):
    purchase = Purchase.get(purchase_id)
    purchase.delete()
    return make_response(jsonify({'message': 'Deleted successfully'})), 204


if __name__ == '__main__':
    User.create_table(read_capacity_units=1, write_capacity_units=1)
    Purchase.create_table(read_capacity_units=1, write_capacity_units=1)
    app.run(debug=True)
