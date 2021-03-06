# Sample API for a Raffle app


## Description
Python API for an E-Raffle app using PynamoDB and Flask with Slam for serverless deployment of Python APIs


## Contents
- [Installation](#Installation)
- [Features](#Features)
- [Database Structure](##database-structure)
- [API Endpoints](##api-endpoints-and-responses)
- [References](##references)


## Installation and Running locally

- `git clone <repo_url>`

- `cd <repo_name>`

- `pip install virtualenv`

- `virtualenv --no-site-packages venv`

- `source venv/bin/activate`

- `pip install -r requirements.txt`

- Download _dynamodb_local_ (see [References](#references))

- Once the file was downloaded, run dynamodb_local `java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb`

- Run `. ./setup.sh` to export environment variables

- Run API locally `python raffle_api.py`

- Access DynamoDB shell `localhost:8000/shell`

- Accessing DynamoDB via CLI `pip install awscli`

- Sample AWS Command `aws dynamodb list-tables --endpoint-url http://localhost:8000`

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
| last_login        |                   |


## Using Slam (for more details please look for Getting Started with Slam in References)

- Configure Slam
    `slam init raffle_api:app --wsgi --stages dev,prod --dynamodb-tables purchases --dynamodb-tables users`

- Setup AWS Credentials
    `pip install awscli`

- Configure AWS
    `aws configure`

    ```
    (venv) $ aws configure
    AWS Access Key ID [None]:
    AWS Secret Access Key [None]:
    Default region name [None]:
    Default output format [None]:
    ```

- Deploy (Sample Scenario)
    ```
    (venv) $ slam deploy
    Building lambda package...
    Deploying simple-api...
    simple-api is deployed!
      dev: https://ukhhy78b6a.execute-api.us-west-2.amazonaws.com/dev
      prod: https://ukhhy78b6a.execute-api.us-west-2.amazonaws.com/prod
    ```

- Publish to `prod`
    ```
    (venv) $ slam publish prod
    Publishing simple-api:dev to prod...
    simple-api is deployed!
      dev: https://ukhhy78b6a.execute-api.us-west-2.amazonaws.com/dev
      prod:1: https://ukhhy78b6a.execute-api.us-west-2.amazonaws.com/prod
    ```

- Check for project status
    ```
    (venv) $ slam status
    simple-api is deployed!
      dev: https://ukhhy78b6a.execute-api.us-west-2.amazonaws.com/dev
      prod:1: https://ukhhy78b6a.execute-api.us-west-2.amazonaws.com/prod
    ```

- Delete project
    `slam delete`


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
    "first_name": "",
    "last_name": "",
    "email": "",
    "password": "",
    "street": "",
    "city": "",
    "gender": "",
    "mobile_number": "",
    "birthday": ""
}
```

### Create new user

```
Endpoint: /user
Method: POST
Body:
{
    "first_name": "",
    "last_name": "",
    "email": "",
    "password": "",
    "street": "",
    "city": "",
    "gender": "",
    "mobile_number": "",
    "birthday": ""
}
```

### Get all purchases of user by user_id

```
Endpoint: /purchases?user_id={id}
Method: GET
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

### Add new purchase by user_id

```
Endpoint: /purchases
Method: POST
Body:
{
    "user_id": "",
    "amount": 3000,
    "store_name": "",
    "card_used": "",
    "transaction_date": "MM/DD/YY",
    "transaction_type": ""
}
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
- [Getting Started with PynamoDB](http://pynamodb.readthedocs.io/en/latest/quickstart.html)
