import jsonpickle, json, datetime, traceback
# from jwt import JWT, exceptions
from flask import request
from functools import wraps
import entitlement, util, errors
# from util import debug_mode, get_public_key, set_account_id
from util import debug_mode, set_account_id

from context import context
import jwt 
import base64
import os
from secrets import read_secret


ALGORITHMS = 'RS256'


def get_token_auth_header():
   
    auth = request.headers.get('authorization', None)
    if not auth:
        raise errors.AuthError('authorization_header_missing. Authorization header is expected', 401)
    token = auth
    return token
  
    
def requires_auth(required_access_level):
    def decorator_requires_auth(f):
        @wraps(f)
        def decorated_requires_auth(*args, **kwargs):
            try:
                if util.debug_mode():
                    util.set_account_id()
                    return f(*args, **kwargs)
                else:
                    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkZXRhaWxzIjp7ImFwaUtleSI6InZzdkluZG9ZRWpKazR2Sk4zR0ZpaFMxcXlEU004Sy9GTzZpN1pleHE3MGdoZFZnY09XNE8xMnZIenJRbVhPaW1nRWxoNjdYbTlSVFc5bXVMUWtSd240S3llbGh3M29NRFZrVldYNEZoMHpLWWVjRXk2Z0Era1VFNTVIRlVtRng2S2JldklBbmhQbGYxRjE2K3hkKzk2Y2RCL2dJNklLdVVTbTBrNmFXRlZxTT0iLCJtZXRhZGF0YSI6bnVsbCwidGVuYW50SUQiOiJUTlRfSE1JWUtYVUZDVzU2V0NFSDJIOUQzOCIsInVpZCI6Im15LXJoZWwtaWNwLWFkbWluIiwidXNlcklEIjoidXNyX01IR0tDUFpUSUJNS1BOSktYVVdOSFIiLCJ1c2VyUHJpdmlsZWdlcyI6WyJwYWdlOi9hY3Rpb25zbGlzdCIsInBhZ2U6L2Fub21hbGllcy1yZXBvcnQiLCJwYWdlOi9hbm9tYWxpZXMiLCJwYWdlOi9ub3RpZmljYXRpb25zL2RldGFpbHMiLCJwYWdlOi9ub3RpZmljYXRpb25zIiwicGFnZTovb3ZlcnZpZXciLCJwYWdlOi9yZXBvcnQiLCJwYWdlOi9yZXBvcnRzIiwicGFnZTovcmlzay9kYXRhb2JqZWN0cyIsInBhZ2U6L3Jpc2svZGF0YXNvdXJjZXMiLCJwYWdlOi9yaXNrL3VzZXJzIiwicGFnZTovc2V0dGluZ3Mvbm90aWZpY2F0aW9ucyIsInBhZ2U6L3NldHRpbmdzL3Byb2ZpbGUiLCJwYWdlOi90aWNrZXRpbmciLCJwZXJtaXNzaW9uOmdyb3VwOmNyZWF0ZSIsInBlcm1pc3Npb246cGFnZTovYWN0aW9uc2xpc3QiLCJwZXJtaXNzaW9uOnBhZ2U6L2Fub21hbGllcy1yZXBvcnQiLCJwZXJtaXNzaW9uOnBhZ2U6L2Fub21hbGllcyIsInBlcm1pc3Npb246cGFnZTovbm90aWZpY2F0aW9ucy9kZXRhaWxzIiwicGVybWlzc2lvbjpwYWdlOi9ub3RpZmljYXRpb25zIiwicGVybWlzc2lvbjpwYWdlOi9vdmVydmlldyIsInBlcm1pc3Npb246cGFnZTovcmVwb3J0IiwicGVybWlzc2lvbjpwYWdlOi9yZXBvcnRzIiwicGVybWlzc2lvbjpwYWdlOi9yaXNrL2RhdGFvYmplY3RzIiwicGVybWlzc2lvbjpwYWdlOi9yaXNrL2RhdGFzb3VyY2VzIiwicGVybWlzc2lvbjpwYWdlOi9yaXNrL3VzZXJzIiwicGVybWlzc2lvbjpwYWdlOi9zZXR0aW5ncy9ub3RpZmljYXRpb25zIiwicGVybWlzc2lvbjpwYWdlOi9zZXR0aW5ncy9wcm9maWxlIiwicGVybWlzc2lvbjpwYWdlOi90aWNrZXRpbmciLCJwZXJtaXNzaW9uOnJlcG9ydDpjcmVhdGUiLCJwZXJtaXNzaW9uOnJlc3RhcGk6L2FwaS92Mi9ncm91cHMiLCJwZXJtaXNzaW9uOnJlc3RhcGk6L2FwaS92Mi9yZXBvcnRzIiwicGVybWlzc2lvbjpyZXN0YXBpOi9hcGkvdjIvdXNlcnMiLCJyZXBvcnQ6MSIsInJlcG9ydDoxMDAxIiwicmVwb3J0OjIiLCJyZXBvcnQ6MjAzIiwicmVwb3J0OjMwMSIsInJlcG9ydDo0MDEiLCJyZXBvcnQ6NzAxIiwicmVwb3J0OjcwMiIsInJlcG9ydDo3MDMiLCJyZXBvcnQ6NzA0IiwicmVwb3J0OjcwNSIsInJlcG9ydDo3MDciLCJyZXBvcnQ6OTAxIiwicmVwb3J0OjkwMyIsInJlcG9ydDo5MDQiLCJyZXBvcnQ6OTA1IiwicmVwb3J0OjkwNiIsInJlcG9ydDo5MDciLCJyZXBvcnQ6OTA4IiwicmVzdGFwaTovYXBpL3YyL2dyb3VwcyIsInJlc3RhcGk6L2FwaS92Mi9yZXBvcnRzIiwicmVzdGFwaTovYXBpL3YyL3VzZXJzIiwicGFnZTovYXBpa2V5cyIsInBhZ2U6L3NldHRpbmdzL2xkYXAiLCJwYWdlOi9zZXR0aW5ncy9yb2xlcyIsInBhZ2U6L3NldHRpbmdzL3VzZXJzIiwicGVybWlzc2lvbjpwYWdlOi9hcGlrZXlzIiwicGVybWlzc2lvbjpwYWdlOi9zZXR0aW5ncy9sZGFwIiwicGVybWlzc2lvbjpwYWdlOi9zZXR0aW5ncy9yb2xlcyIsInBlcm1pc3Npb246cGFnZTovc2V0dGluZ3MvdXNlcnMiXSwidXNlclJvbGVzIjoic3VwZXIgYWRtaW4ifSwiZXhwIjoxNTk3MDg2MzgzLCJpc3MiOiJ0ZW5hbnR1c2VyIn0.WTHbfSd-MjhJIeJKYVgtewHPax3eJKrt0H2eJsLE8lo"      
                    secretKey=read_secret()
                    # secretKey=os.environ.get('_TENANT_USER_SECRET')
                    print ("please show me the secretKey")
                    print (secretKey)                    
                    try:
                        # payload = jwt.decode(
                        #     token,
                        #     rsa_key,
                        #     ALGORITHMS
                        # )
                        # payload = jwt.decode(token, secretKey,algorithms='HS256')

                        payload = jwt.decode(token, base64.b64decode(secretKey),algorithms='HS256')
                       
                    except Exception as e:
                        context().logger.exception(e)
                        context().logger.error(traceback.format_exc())
                        # raise jwt.exceptions.ExpiredSignatureError('Signature has expired. Unable to parse authentication token.', 401)
                        raise errors.AuthError('invalid_header. unsupported the public key format ', 401)

                    # util.set_account_id(payload['isc_account'])
                    exp = payload['exp']
                    # iat = payload['iat']
                    if (exp < int(datetime.datetime.now().strftime('%s'))):
                        raise errors.AuthError('token_expired. token is expired', 401)
                    entitlement.entitlementCheck(token, payload, required_access_level)

                    return f(*args, **kwargs)
            finally:
                context().account_id = None

        return decorated_requires_auth
    return decorator_requires_auth



# def get_token_auth_header_old():
#     auth = request.headers.get('Authorization', None)
#     print (auth)
#     auth="Bearer bXktcmhlbC1pY3AtYWRtaW46QUhpcHBvcG90YW11c1BsYXlzSG9wc2NvdGNoV2l0aEFuRWxlcGhhbnQ="
#     if not auth:
#         raise errors.AuthError('authorization_header_missing. Authorization header is expected', 401)
#     parts = auth.split()
#     if parts[0].lower() != 'bearer':
#         raise errors.AuthError('invalid_header. Authorization header must start with Bearer', 401)
#     elif len(parts) == 1:
#         raise  errors.AuthError('invalid_header. Token not found', 401)
#     elif len(parts) > 2:
#         raise errors.AuthError('invalid_header. Authorization header must be Bearer token', 401)
#     token = parts[1]
#     print (token)
#     return token


# def requires_auth_old(required_access_level):
#     def decorator_requires_auth(f):
#         @wraps(f)
#         def decorated_requires_auth(*args, **kwargs):
#             try:
#                 if util.debug_mode():
#                     util.set_account_id()
#                     return f(*args, **kwargs)
#                 else:
#                     token = get_token_auth_header()
#                     try:
#                         rsa_key = util.get_public_key()
#                     except exceptions.UnsupportedKeyTypeError as e:
#                         context().logger.exception(e)
#                         context().logger.error(traceback.format_exc())
#                         raise errors.AuthError('invalid_header. unsupported the public key format ', 401)

#                     if not rsa_key:
#                         raise errors.AuthError('RSA key is not found.', 401)

#                     try:
#                         payload = JWT().decode(
#                             token,
#                             rsa_key,
#                             ALGORITHMS
#                         )
#                     except Exception as e:
#                         context().logger.exception(e)
#                         context().logger.error(traceback.format_exc())
#                         raise errors.AuthError('invalid_header. Unable to parse authentication token.', 401)

#                     util.set_account_id(payload['isc_account'])

#                     exp = payload['exp']
#                     iat = payload['iat']
#                     if (iat > int(datetime.datetime.now().strftime('%s')) or exp < int(datetime.datetime.now().strftime('%s'))):
#                         raise errors.AuthError('token_expired. token is expired', 401)

#                     entitlement.entitlementCheck(token, payload, required_access_level)

#                     return f(*args, **kwargs)
#             finally:
#                 context().account_id = None

#         return decorated_requires_auth
#     return decorator_requires_auth
