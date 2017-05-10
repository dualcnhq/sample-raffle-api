# SM E-Raffle API

## Description
Python Serverless API for SM E-Raffle

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
| gender            | campaign          |
| mobile_number     |  - id             |
| birthday          |  - name           |
| accepted_terms    |                   |
|  - campaign_ids   |                   |
| date_created      |                   |
| date_updated      |                   |


## API Endpoints and Responses

`Get user details`

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

`Update user details`

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

`Create new user`

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

`Get all purchases of user by user_id`

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

`Delete a specific purchase item`

```
Endpoint: /purchases/{id}
Method: DELETE
Params: purchase_id
```

## Ideal Application Architecture
- RestAPI (back-end code)
- Events
- Utils


## References
- [Serverless Architecture Code Patterns](https://serverless.com/blog/serverless-architecture-code-patterns/)
