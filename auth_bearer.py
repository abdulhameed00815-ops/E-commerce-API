from fastapi import Request, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from auth_handler import decode_jwt


#the init method function auto raises an error if something goes wrong (ex: the whole token is missing)
class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)
    

#this function is a long one, it checks for 2 stuff, firstly for the header of the token, if it is not a Bearer then access is denied, and then checks if the token is expired (via the verify_jwt function) then also the access is denied
#the call method makes the class callable just like a function    
    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="invalid authorization code.")
        

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decode_jwt(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid


class IsAdmin(JWTBearer):
    async def __call__(self, request: Request):
        token = await super().__call__(request)
        payload = decode_jwt(token)
        if payload.get("role") == 'admin':
            return True 
        else:
            raise HTTPException(status_code=403, detail="access denied bitch") 
