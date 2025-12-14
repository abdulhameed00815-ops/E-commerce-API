Summary of the Project:
This is an ecommerce api (amazon clone) that i made in about 7 weeks.

Project features:
1-signup and signin functionality.
2-cart functionality and product browsing.
3-checkout functionality.
4-admin functionality to add/remove products.
5-jwt authentication for securing routes.

Project stack:
1-python for the backend.
2-python's fastapi framework is used.
3-javascript, html and css are used for making the client.
4-postgres' sqlalchemy orm is used for databases.
5-bcrypt is used for encoding/decoding passwords.
6-stripe api is used for checkout flow.

Project Requirements:
1-postgresql.
2-sqlalchemy.
#the following require a venv:
3-fastapi[standard].
4-bcrypt.
5-python-decouple.
6-stripe.
7-re.
8-fastapi_jwt_auth2.

Other Requirements:
1-a .env file with the following stuff:
secret=any_secret_string
algorithm=HS256
stripeSecretKey=your_stripe_secret_key (works only in test mode)
masterkey=whatever_Secret_you_want
2-a test stripe account with a secret key and a publishable key.

Notes on the Project:
1-all features work fine, but some features wont handle errors gracefully (a refresh can fix that).

To run this Project:
1-you must meet all the requirements (there might be ones that i forgot to mention, but can be easily diagnosed by simply running "users.py".
2-you have to start "users.py" as a server using fastapi (fastapi dev users.py).
3-you must run a localhost http server for your client (python3 -m http.server 5500).
4-you have to pray.
