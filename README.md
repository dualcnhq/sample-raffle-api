# SM E-Raffle API


## Description
Python Serverless API for SM E-Raffle


## Features

- User registration
- User login
- Input Receipt
- Show Number of Entries
- Export data as CSV
    - Entries
    - Participants (CSV)


## Database Structure


| User          | Purchases     | Redemptions     |
|---------------|---------------|-----------------|
| id            | id            | id              |
| firstName     | user_id       | user_id         |
| lastName      | amount        | redemption_code |
| email         | store_name    | date_redeemed   |
| address       | date_created  | date_created    |
| date_created  |               |                 |
