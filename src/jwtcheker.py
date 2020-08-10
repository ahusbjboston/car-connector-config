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
                    # token = get_token_auth_header()
                    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkZXRhaWxzIjp7ImFwaUtleSI6IkFoaVBZZm5Yd0xDM0N4a1pIb3drejg3dWhYNDRMSUtWTmVFb3BNLzZiRE5xM1VXNlVlNGJRTXQ2T1YxVEVGQ0Zya1Y5OEZiTTFJbEtaZHpsa3BVSzBwSTZYV2JETXVtOVdEOTREUklXQWJleVcxejl2T0dGdDVFK0ZXSm1TRDV5QStxRkg4ZEVGcTJLOHc0RlptK2prYVdMTkI0S2lXdHlOSUNOUFd0Ukh0dz0iLCJtZXRhZGF0YSI6bnVsbCwidGVuYW50SUQiOiJUTlRfT1daWVY0SFVXRFRMVVNEUE1CU1VLIiwidWlkIjoibXktcmhlbC1pY3AtYWRtaW4iLCJ1c2VySUQiOiJ1c3JfRkRZQVdQUEVVREpQUU5KM1NZUlVUTSIsInVzZXJQcml2aWxlZ2VzIjpbInBhZ2U6L2FjdGlvbnNsaXN0IiwicGFnZTovYW5vbWFsaWVzLXJlcG9ydCIsInBhZ2U6L2Fub21hbGllcyIsInBhZ2U6L25vdGlmaWNhdGlvbnMvZGV0YWlscyIsInBhZ2U6L25vdGlmaWNhdGlvbnMiLCJwYWdlOi9vdmVydmlldyIsInBhZ2U6L3JlcG9ydCIsInBhZ2U6L3JlcG9ydHMiLCJwYWdlOi9yaXNrL2RhdGFvYmplY3RzIiwicGFnZTovcmlzay9kYXRhc291cmNlcyIsInBhZ2U6L3Jpc2svdXNlcnMiLCJwYWdlOi9zZXR0aW5ncy9ub3RpZmljYXRpb25zIiwicGFnZTovc2V0dGluZ3MvcHJvZmlsZSIsInBhZ2U6L3RpY2tldGluZyIsInBlcm1pc3Npb246Z3JvdXA6Y3JlYXRlIiwicGVybWlzc2lvbjpwYWdlOi9hY3Rpb25zbGlzdCIsInBlcm1pc3Npb246cGFnZTovYW5vbWFsaWVzLXJlcG9ydCIsInBlcm1pc3Npb246cGFnZTovYW5vbWFsaWVzIiwicGVybWlzc2lvbjpwYWdlOi9ub3RpZmljYXRpb25zL2RldGFpbHMiLCJwZXJtaXNzaW9uOnBhZ2U6L25vdGlmaWNhdGlvbnMiLCJwZXJtaXNzaW9uOnBhZ2U6L292ZXJ2aWV3IiwicGVybWlzc2lvbjpwYWdlOi9yZXBvcnQiLCJwZXJtaXNzaW9uOnBhZ2U6L3JlcG9ydHMiLCJwZXJtaXNzaW9uOnBhZ2U6L3Jpc2svZGF0YW9iamVjdHMiLCJwZXJtaXNzaW9uOnBhZ2U6L3Jpc2svZGF0YXNvdXJjZXMiLCJwZXJtaXNzaW9uOnBhZ2U6L3Jpc2svdXNlcnMiLCJwZXJtaXNzaW9uOnBhZ2U6L3NldHRpbmdzL25vdGlmaWNhdGlvbnMiLCJwZXJtaXNzaW9uOnBhZ2U6L3NldHRpbmdzL3Byb2ZpbGUiLCJwZXJtaXNzaW9uOnBhZ2U6L3RpY2tldGluZyIsInBlcm1pc3Npb246cmVwb3J0OmNyZWF0ZSIsInBlcm1pc3Npb246cmVzdGFwaTovYXBpL3YyL2dyb3VwcyIsInBlcm1pc3Npb246cmVzdGFwaTovYXBpL3YyL3JlcG9ydHMiLCJwZXJtaXNzaW9uOnJlc3RhcGk6L2FwaS92Mi91c2VycyIsInJlcG9ydDoxIiwicmVwb3J0OjEwMDEiLCJyZXBvcnQ6MiIsInJlcG9ydDoyMDMiLCJyZXBvcnQ6MzAxIiwicmVwb3J0OjQwMSIsInJlcG9ydDo3MDEiLCJyZXBvcnQ6NzAyIiwicmVwb3J0OjcwMyIsInJlcG9ydDo3MDQiLCJyZXBvcnQ6NzA1IiwicmVwb3J0OjcwNyIsInJlcG9ydDo5MDEiLCJyZXBvcnQ6OTAzIiwicmVwb3J0OjkwNCIsInJlcG9ydDo5MDUiLCJyZXBvcnQ6OTA2IiwicmVwb3J0OjkwNyIsInJlcG9ydDo5MDgiLCJyZXN0YXBpOi9hcGkvdjIvZ3JvdXBzIiwicmVzdGFwaTovYXBpL3YyL3JlcG9ydHMiLCJyZXN0YXBpOi9hcGkvdjIvdXNlcnMiLCJwYWdlOi9hdWRpdCIsInBhZ2U6L2F3c2tpbmVzaXNsaXN0IiwicGFnZTovYXp1cmVvdmVydmlldyIsInBhZ2U6L2Nvbm5lY3Rpb25zIiwicGFnZTovZ2V0LXN0YXJ0ZWQiLCJwYWdlOi9ncm91cHMvZ3JvdXBidWlsZGVyIiwicGFnZTovZ3JvdXBzIiwicGFnZTovZ3VhcmRpdW1jZW50cmFsbWFuYWdlcnMiLCJwYWdlOi9ndWFyZGl1bW1hbmFnZWR1bml0cyIsInBhZ2U6L3NldHRpbmdzL3N0b3JhZ2UiLCJwZXJtaXNzaW9uOmdyb3VwOioiLCJwZXJtaXNzaW9uOnBhZ2U6L2F1ZGl0IiwicGVybWlzc2lvbjpwYWdlOi9hd3NraW5lc2lzbGlzdCIsInBlcm1pc3Npb246cGFnZTovYXp1cmVvdmVydmlldyIsInBlcm1pc3Npb246cGFnZTovY29ubmVjdGlvbnMiLCJwZXJtaXNzaW9uOnBhZ2U6L2dldC1zdGFydGVkIiwicGVybWlzc2lvbjpwYWdlOi9ncm91cHMvZ3JvdXBidWlsZGVyIiwicGVybWlzc2lvbjpwYWdlOi9ncm91cHMiLCJwZXJtaXNzaW9uOnBhZ2U6L2d1YXJkaXVtY2VudHJhbG1hbmFnZXJzIiwicGVybWlzc2lvbjpwYWdlOi9ndWFyZGl1bW1hbmFnZWR1bml0cyIsInBlcm1pc3Npb246cGFnZTovc2V0dGluZ3Mvc3RvcmFnZSIsInBlcm1pc3Npb246cmVwb3J0OjEiLCJwZXJtaXNzaW9uOnJlcG9ydDoxMDAxIiwicGVybWlzc2lvbjpyZXBvcnQ6MiIsInBlcm1pc3Npb246cmVwb3J0OjIwMyIsInBlcm1pc3Npb246cmVwb3J0OjMwMSIsInBlcm1pc3Npb246cmVwb3J0OjQwMSIsInBlcm1pc3Npb246cmVwb3J0OjcwMSIsInBlcm1pc3Npb246cmVwb3J0OjcwMiIsInBlcm1pc3Npb246cmVwb3J0OjcwMyIsInBlcm1pc3Npb246cmVwb3J0OjcwNCIsInBlcm1pc3Npb246cmVwb3J0OjcwNSIsInBlcm1pc3Npb246cmVwb3J0OjcwNyIsInBlcm1pc3Npb246cmVwb3J0OjkwMSIsInBlcm1pc3Npb246cmVwb3J0OjkwMyIsInBlcm1pc3Npb246cmVwb3J0OjkwNCIsInBlcm1pc3Npb246cmVwb3J0OjkwNSIsInBlcm1pc3Npb246cmVwb3J0OjkwNiIsInBlcm1pc3Npb246cmVwb3J0OjkwNyIsInBlcm1pc3Npb246cmVwb3J0OjkwOCIsInBlcm1pc3Npb246cmVwb3J0OioiLCJwYWdlOi9hcGlrZXlzIiwicGFnZTovc2V0dGluZ3MvbGRhcCIsInBhZ2U6L3NldHRpbmdzL3JvbGVzIiwicGFnZTovc2V0dGluZ3MvdXNlcnMiLCJwZXJtaXNzaW9uOnBhZ2U6L2FwaWtleXMiLCJwZXJtaXNzaW9uOnBhZ2U6L3NldHRpbmdzL2xkYXAiLCJwZXJtaXNzaW9uOnBhZ2U6L3NldHRpbmdzL3JvbGVzIiwicGVybWlzc2lvbjpwYWdlOi9zZXR0aW5ncy91c2VycyJdLCJ1c2VyUm9sZXMiOiJzdXBlciBhZG1pbixhZG1pbiJ9LCJleHAiOjE1OTcwMzc2NTUsImlzcyI6InRlbmFudHVzZXIifQ.r09IDlNpanu-LzzDq5JUAgF22fWHz7UVGkbEJw2X7kM"                   
                    secretKey=read_secret()
                    # secretKey=os.environ.get('_TENANT_USER_SECRET')
                    print ("please show me the secretKey")
                    print (secretKey)
                    # print (os.environ.get('TENANT_USER_SECRET'))
                    
                    try:
                        # payload = jwt.decode(
                        #     token,
                        #     rsa_key,
                        #     ALGORITHMS
                        # )
                        payload = jwt.decode(token, secretKey,algorithms='HS256')

                        # payload = jwt.decode(token, base64.b64decode(secretKey),algorithms='HS256')
                       
                    except Exception as e:
                        context().logger.exception(e)
                        context().logger.error(traceback.format_exc())
                        raise errors.AuthError('invalid_header. Unable to parse authentication token.', 401)

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
