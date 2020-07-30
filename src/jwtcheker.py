import jsonpickle, json, datetime, traceback
from jwt import JWT, exceptions
from flask import request
from functools import wraps

import entitlement, util, errors
from util import debug_mode, get_public_key, set_account_id
from context import context

ALGORITHMS = 'RS256'

def get_token_auth_header():
    auth = request.headers.get('Authorization', None)
    print (auth)
    auth="Bearer bXktcmhlbC1pY3AtYWRtaW46QUhpcHBvcG90YW11c1BsYXlzSG9wc2NvdGNoV2l0aEFuRWxlcGhhbnQ="
    if not auth:
        raise errors.AuthError('authorization_header_missing. Authorization header is expected', 401)
    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise errors.AuthError('invalid_header. Authorization header must start with Bearer', 401)
    elif len(parts) == 1:
        raise  errors.AuthError('invalid_header. Token not found', 401)
    elif len(parts) > 2:
        raise errors.AuthError('invalid_header. Authorization header must be Bearer token', 401)
    token = parts[1]
    print (token)
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
                    token = get_token_auth_header()
                    try:
                        rsa_key = util.get_public_key()
                    except exceptions.UnsupportedKeyTypeError as e:
                        context().logger.exception(e)
                        context().logger.error(traceback.format_exc())
                        raise errors.AuthError('invalid_header. unsupported the public key format ', 401)

                    if not rsa_key:
                        raise errors.AuthError('RSA key is not found.', 401)

                    try:
                        payload = JWT().decode(
                            token,
                            rsa_key,
                            ALGORITHMS
                        )
                    except Exception as e:
                        context().logger.exception(e)
                        context().logger.error(traceback.format_exc())
                        raise errors.AuthError('invalid_header. Unable to parse authentication token.', 401)

                    util.set_account_id(payload['isc_account'])

                    exp = payload['exp']
                    iat = payload['iat']
                    if (iat > int(datetime.datetime.now().strftime('%s')) or exp < int(datetime.datetime.now().strftime('%s'))):
                        raise errors.AuthError('token_expired. token is expired', 401)

                    entitlement.entitlementCheck(token, payload, required_access_level)

                    return f(*args, **kwargs)
            finally:
                context().account_id = None

        return decorated_requires_auth
    return decorator_requires_auth
