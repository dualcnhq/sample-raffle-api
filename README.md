# SM E-Raffle API


## Description
Python Serverless API for SM E-Raffle

## Installation

`git clone <repo_url>`
`cd <repo_name>`
`pip install virtualenv`
`virtualenv --no-site-packages venv`
`source venv/bin/activate`
`pip install -r requirements.txt`



## Features
- User registration
- User login
- Input Receipt
- Export data as CSV
    - Entries
    - Participants
- Show Number of Entries
    - Generated based on Purchases
- Generate printable coupon
- Create a campaign id and name (hard-coded)

## Database Structure
| User              | Purchases         |
|-------------------|-------------------|
| id                | id                |
| first_name        | user_id           |
| last_name         | amount            |
| email             | store_name        |
| pasword           | card_used         |
| address           | transaction_date  |
|  - street         | transaction_type  |
|  - city           | date_created      |
| num_entries       | campaign          |
| gender            |  - id             |
| mobile_number     |  - name           |
| birthday          |                   |
| accepted_terms    |                   |
|  - campaign_ids   |                   |
| date_created      |                   |
| date_updated      |                   |


## API Endpoints and Responses


### Get user details

```
Endpoint: /user/{id}
Method: GET
Params: user_id

Expected Response:
{
    "id": "",
    "first_name": "",
    "last_name": "",
    "email": "",
    "password": "",
    "address": {
        "street": "",
        "city": "",
    },
    "gender": "",
    "mobile_number": "",
    "birthday": "",
    "accepted_terms": {
        "campaign_id": ""
    },
    "date_created": "",
    "date_updated": "",
    "last_login": "",
}
```

### Update user details

```
Endpoint: /user/{id}
Method: PUT
Params: user_id
Body:
{
    "id": "",
    "first_name": "",
    "last_name": "",
    "email": "",
    "password": "",
    "address": {
        "street": "",
        "city": "",
    },
    "gender": "",
    "mobile_number": "",
    "birthday": ""
}
```

### Create new user

```
Endpoint: /user/user
Method: POST
Body:
{
    "first_name": "",
    "last_name": "",
    "email": "",
    "password": "",
    "address": {
        "street": "",
        "city": "",
    },
    "gender": "",
    "mobile_number": "",
    "birthday": ""
}
```

### Get all purchases of user by user_id

```
Endpoint: /purchases?user_id={id}
Params: user_id
Expected Response:
[
    {
        "id": "",
        "user_id": "",
        "amount": 1000,
        "store_name": "",
        "card_used": "",
        "transaction_date": "",
        "transaction_type": "",
        "date_created": "",
        "campaign": {
            "id": "",
            "name": ""
        }
    }
]
```

### Delete a specific purchase item

```
Endpoint: /purchases/{id}
Method: DELETE
Params: purchase_id
```

### Login

```
Endpoint: /login
Method: POST
Params:
```

### Forgot Password

```
Endpoint: /forgot_password
Method: POST
Params:
```

## Ideal Application Architecture
- RestAPI (back-end code)
- Events
- Utils


## References
- [Serverless Architecture Code Patterns](https://serverless.com/blog/serverless-architecture-code-patterns/)
- [Setting Up DynamoDB Local](http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html)

- [Getting Started with Slam](http://slam-python.readthedocs.io/en/latest/tutorial.html)
