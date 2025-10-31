import jwt
from decouple import config
import time
from typing import Dict


#we use config from decouple to access environmental variables
JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")


#this is a helper function to return the encoded tokens
def token_response(token: str):
    return {
        "access token": token
    }


#this function creates the token, then uses the token_response function to return it to the user (usually after signing up or in)
def sign_jwt(user_id: str) -> Dict[str, str]:
    payload = {
        "id": user_id,
        "role": role, 
        "expires": time.time() + 600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token_response(token)


#this function decodes the token only if it has NOT expired
def decode_jwt(token: str) -> Dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}
