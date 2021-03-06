#!/usr/bin/env python
import boto3
import datetime
import os
import re
import uuid

from flask import Flask, jsonify, abort, request, make_response, url_for, g
from flask_cors import CORS, cross_origin
from flask_httpauth import HTTPTokenAuth
from itsdangerous import TimedJSONWebSignatureSerializer as JWT
from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute, MapAttribute, ListAttribute
)
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection, LocalSecondaryIndex
from pytz import timezone
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '')
jwt = JWT(app.config['SECRET_KEY'], expires_in=3600)
CORS(app)

auth = HTTPTokenAuth('Bearer')

# Database Model
class UserEmailViewIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "view_index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()
    email = UnicodeAttribute(hash_key=True)

class User(Model):
    class Meta:
        table_name = 'Users'
        region = boto3.Session().region_name
        host = 'http://localhost:8000' \
            if not os.environ.get('LAMBDA_TASK_ROOT') else None
    id = UnicodeAttribute(hash_key=True)
    first_name = UnicodeAttribute()
    last_name = UnicodeAttribute()
    email = UnicodeAttribute()
    password = UnicodeAttribute()
    address = MapAttribute()
    gender = UnicodeAttribute()
    mobile_number = UnicodeAttribute()
    birthday = UnicodeAttribute()
    accepted_terms = MapAttribute()
    email_view_index = UserEmailViewIndex()
    date_created = UTCDateTimeAttribute()
    date_updated = UTCDateTimeAttribute()
    last_login = UTCDateTimeAttribute()


class PurchaseUserViewIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "view_index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()
    user_id = UnicodeAttribute(hash_key=True)

class Purchase(Model):
    class Meta:
        table_name = 'Purchases'
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
    num_of_entries = NumberAttribute(default=0)
    campaign = MapAttribute()
    user_view_index = PurchaseUserViewIndex()
    date_created = UTCDateTimeAttribute()

# Auth & Response Messages
@auth.verify_token
def verify_token(token):
    g.email = None
    try:
        data = jwt.loads(token)
    except:
        return False
    if 'email' in data:
        g.email = data['email']
        return True

    return False

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
        'num_of_entries': purchase.num_of_entries,
        'date_created': purchase.date_created,
        'campaign': {
            'id': deserialized_campaign['campaign_id'],
            'name': deserialized_campaign['campaign_name']
        }
    }

def delete_purchases_linked_to_user(user_id):
    for purchase in Purchase.query(user_id__eq=user_id):
        purchase.delete()

def isEmailValid(email):
    return re.match('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email) != None

## Endpoints
@app.route('/', methods=['GET'])
def index():
    print('SECRET_KEY', os.environ.get('SECRET_KEY'))
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
    data = request.get_json()

    if data is None or 'email' not in data or 'password' not in data:
        abort(400)

    for user in User.email_view_index.query(data.get('email')):
        if check_password_hash(user.password, data.get('password')):
            token = jwt.dumps({'email': data.get('email')})
            return jsonify({'user': make_user(User.get(user.id)), 'token': token})
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
def create_user():
    attr = MapAttribute()
    dt = datetime.datetime.now(timezone('Asia/Manila')) #.strftime("%Y-%m-%d %H:%M:%S")
    data = request.get_json()

    if data is None or 'first_name' not in data:
        abort(400)

    if not isEmailValid(data['email']):
        return jsonify({'error': 'Invalid email address format'}), 400

    address_attribute = {
        'street' : data.get('street', ''),
        'city': data.get('city', '')
    }

    campaign_attribute = {
        'campaign_id' : '502ab6e7a856b67323a7206d74739118',
        'campaign_name': '30thingstodoatmega'
    }

    serialized_address = attr.serialize(address_attribute)
    serialized_campaign = attr.serialize(campaign_attribute)

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
        return jsonify({'purchases': [make_purchase(purchase) for purchase in Purchase.user_view_index.query(user_id)]})

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
        'campaign_name': 'sample_campaign'
    }

    serialized_campaign = attr.serialize(campaign_attribute)

    if data is None or 'amount' not in data:
        abort(400)

    if data.get('amount') >= 3000 and data.get('card_used') != 'Paylite':
        entries = 1
    elif data.get('amount') >= 3000 and data.get('card_used') == 'Paylite':
        entries = 2

    purchase = Purchase(id = uuid.uuid4().hex,
                user_id = data.get('user_id', ''),
                amount = data.get('amount', 0),
                store_name = data.get('store_name', ''),
                card_used = data.get('card_used', ''),
                transaction_date = data.get('transaction_date', ''),
                transaction_type = data.get('transaction_type', ''),
                campaign = serialized_campaign,
                num_of_entries = entries,
                date_created = dt)
    purchase.save()
    return jsonify({'purchase': make_purchase(purchase)}), 201

@app.route('/purchases/<purchase_id>', methods=['DELETE'])
@auth.login_required
def delete_purchase(purchase_id):
    purchase = Purchase.get(purchase_id)
    purchase.delete()
    return jsonify({'message': 'Purchase record was deleted'}), 200

if __name__ == '__main__':
    User.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
    Purchase.create_table(read_capacity_units=1, write_capacity_units=1)
    app.run(debug=True)
