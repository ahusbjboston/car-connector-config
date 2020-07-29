import traceback
from functools import wraps
from kubernetes.client.rest import ApiException

from context import context

def error_handler(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ApiException as e:
            context().logger.exception(e)
            context().logger.error(traceback.format_exc())
            return e.body, e.status
        except ValueError as e:
            context().logger.exception(e)
            context().logger.error(traceback.format_exc())
            return str(e.args), 400
        except AuthError as e:
            context().logger.exception(e)
            context().logger.error(traceback.format_exc())
            return e.error, 401
        except Exception as e:
            context().logger.exception(e)
            context().logger.error(traceback.format_exc())
            raise e
    return wrapper

class AuthError(Exception):
    def __init__(self, message, status_code):
        self.error = (f'Authorization Error: {message}')
        self.status_code = status_code
