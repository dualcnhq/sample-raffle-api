#!/usr/bin/env python
import boto3
import datetime
import os
import re
import uuid

from flask import Flask, jsonify, abort, request, make_response, url_for
from flask_httpauth import HTTPBasicAuth
from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute, MapAttribute
)
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
    num_of_entries = NumberAttribute(default=0)
    address = MapAttribute()
    gender = UnicodeAttribute()
    mobile_number = UnicodeAttribute()
    birthday = UnicodeAttribute()
    accepted_terms = MapAttribute()
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
    campaign = MapAttribute()
    date_created = UTCDateTimeAttribute()

# Auth & Response Messages
@auth.get_password
def get_password(email):  # TODO
    print('email', email)

    for user in User.scan(email__eq=email):
        print('user', user.email)
        print('userPassword', user.password)
        print('passwordHash', check_password_hash(user.password, 'test'))

    if email == 'admin':
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
    attr = MapAttribute()

    deserialized_address = attr.deserialize(user.address)
    deserialized_campaign = attr.deserialize(user.accepted_terms)

    return {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'password': user.password,
        'address': {
            'street': deserialized_address['street'],
            'city':  deserialized_address['city']
        },
        'num_of_entries': user.num_of_entries,
        'gender': user.gender,
        'mobile_number': user.mobile_number,
        'birthday': user.birthday,
        'accepted_terms': {
            'campaign_id': deserialized_campaign['campaign_id'],
            'campaign_name': deserialized_campaign['campaign_name']
        },
        'date_created': user.date_created,
        'date_updated': user.date_updated,
        'last_login': user.last_login
    }

def make_purchase(purchase):
    attr = MapAttribute()
    deserialized_campaign = attr.deserialize(purchase.campaign)

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
            'id': deserialized_campaign['campaign_id'],
            'name': deserialized_campaign['campaign_name']
        }
    }

def update_user_raffle_entries(user_id, entry):
    user = User.get(user_id)
    user.num_of_entries = user.num_of_entries + entry
    user.save()

def delete_purchases_linked_to_user(user_id):
    for purchase in Purchase.scan(user_id__eq=user_id):
        purchase.delete()

def isEmailValid(email):
    return re.match('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email) != None

## Endpoints
@app.route('/', methods=['GET'])
def index():
    return jsonify(
        {
            'name': 'users',
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
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        for user in User.scan(email__eq=data.get('email')):
            if check_password_hash(user.password, data.get('password')):
                return jsonify({'user': make_user(User.get(user.id))})
            else:
                return jsonify({'error': 'Wrong password'}), 400

        return jsonify({'error': 'Invalid user credentials'}), 400


@app.route('/users', methods=['GET'])
@auth.login_required
def get_users():
    return jsonify({'users': [make_user(user) for user in User.scan()]})

@app.route('/users/<user_id>', methods=['GET'])
@auth.login_required
def get_user(user_id):
    return jsonify({'user': make_user(User.get(user_id))})

@app.route('/users', methods=['POST'])
# @auth.login_required - no auth required in creating new user
def create_user():
    dt = datetime.datetime.now(timezone('Asia/Manila')) #.strftime("%Y-%m-%d %H:%M:%S")
    data = request.get_json()

    address_attribute = {
        'street' : data.get('street', ''),
        'city': data.get('city', '')
    }

    campaign_attribute = {
        'campaign_id' : '502ab6e7a856b67323a7206d74739118',
        'campaign_name': '30thingstodoatmega'
    }

    attr = MapAttribute()
    serialized_address = attr.serialize(address_attribute)
    serialized_campaign = attr.serialize(campaign_attribute)

    if data is None or 'first_name' not in data:
        abort(400)

    if not isEmailValid(data['email']):
        return jsonify({'error': 'Invalid email address format'}), 400

    user = User(
        id = uuid.uuid4().hex,
        first_name = data.get('first_name', ''),
        last_name = data.get('last_name', ''),
        email = data.get('email', ''),
        password = generate_password_hash(data.get('password', '')),
        gender = data.get('gender', ''),
        mobile_number = data.get('mobile_number', ''),
        birthday = data.get('birthday', ''),
        address = serialized_address,
        accepted_terms = serialized_campaign,
        date_created = dt,
        date_updated = dt,
        last_login = dt)
    user.save()
    return jsonify({'user': make_user(user)}), 201

@app.route('/users/<user_id>', methods=['PUT'])
@auth.login_required
def update_user(user_id):
    attr = MapAttribute()
    data = request.get_json()
    dt = datetime.datetime.now(timezone('Asia/Manila'))
    user = User.get(user_id)

    if not data:
        abort(400)

    if not isEmailValid(data['email']):
        return jsonify({'error': 'Invalid email address format'}), 400

    deserialized_address = attr.deserialize(user.address)

    address_attribute = {
        'street' : data.get('street', deserialized_address['street'] or ''),
        'city': data.get('city', deserialized_address['city'] or '')
    }

    serialized_address = attr.serialize(address_attribute)

    user.first_name = data.get('first_name', user.first_name or '')
    user.last_name = data.get('last_name', user.last_name or '')
    user.email = data.get('email', user.email or '')
    user.password = generate_password_hash(data.get('password', user.password or ''))
    user.address = serialized_address
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
    delete_purchases_linked_to_user(user_id)
    return jsonify({'message': 'User record was deleted'}), 200

## Purchases Endpoint
@app.route('/purchases', methods=['GET'])
@auth.login_required
def get_purchases():
    user_id = request.args.get('user_id')      # get query param => ?user_id=<user_id>
    if user_id is None:
        return jsonify({'purchases': [make_purchase(purchase) for purchase in Purchase.scan()]})
    else:
        return jsonify({'purchases': [make_purchase(purchase) for purchase in Purchase.scan(user_id__eq=user_id)]})

@app.route('/purchases/<purchase_id>', methods=['GET'])
@auth.login_required
def get_purchase(purchase_id):
    return jsonify({'purchase': make_purchase(Purchase.get(purchase_id))})

@app.route('/purchases', methods=['POST'])
@auth.login_required
def create_purchase():
    attr = MapAttribute()
    dt = datetime.datetime.now(timezone('Asia/Manila'))
    data = request.get_json()

    campaign_attribute = {
        'campaign_id' : '502ab6e7a856b67323a7206d74739118',
        'campaign_name': '30thingstodoatmega'
    }

    serialized_campaign = attr.serialize(campaign_attribute)

    if data is None or 'amount' not in data:
        abort(400)

    purchase = Purchase(id = uuid.uuid4().hex,
                user_id = data.get('user_id', ''),
                amount = data.get('amount', 0),
                store_name = data.get('store_name', ''),
                card_used = data.get('card_used', ''),
                transaction_date = data.get('transaction_date', ''),
                transaction_type = data.get('transaction_type', ''),
                campaign = serialized_campaign,
                date_created = dt)
    purchase.save()

    if data.get('amount') >= 3000 and data.get('card_used') == 'Citibank':
        update_user_entries(data.get('user_id'), 1)
    elif data.get('amount') >= 3000 and data.get('card_used') == 'Citibank Paylite':
        update_user_entries(data.get('user_id'), 2)

    return jsonify({'purchase': make_purchase(purchase)}), 201

@app.route('/purchases/<purchase_id>', methods=['DELETE'])
@auth.login_required
def delete_purchase(purchase_id):
    purchase = Purchase.get(purchase_id)
    purchase.delete()
    return jsonify({'message': 'Purchase record was deleted'}), 200

if __name__ == '__main__':
    User.create_table(read_capacity_units=1, write_capacity_units=1)
    Purchase.create_table(read_capacity_units=1, write_capacity_units=1)
    app.run(debug=True)
