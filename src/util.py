import os, requests, time, json, base64
from os.path import dirname, split, join, realpath
# from jwt import jwk_from_pem
from flask import request
from kubernetes.client.rest import ApiException

from context import context

RESOURCES = 'resources'
DEBUG_NAMESPACE = 'CAR_CONNECTOR_CONFIG_NAMESPACE'
DEBUG_PUBLIC_KEY='JWT_PUBLIC_KEY'
DEFAULT_JWT_PUBLIC_KEY='/etc/config/jwt.public.pem'
CAR_TEST_ACCOUNT_ID = 'CAR_TEST_ACCOUNT_ID'
API_KEY_GENERATION_URL = 'API_KEY_GENERATION_URL'
CAR_API_PATH = 'CAR_API_PATH'
APP_FQDN = 'APP_FQDN'


def ignore_404(f):
    try:
        return f()
    except ApiException as e:
        if e.status != 404:
            raise e


# DELETE followed by POST may cause 409 because k8s takes some time for deleting the resource.
# This should be handled by re-attempting POST.
def handle_409(f):
    for i in range(30): # Try for 30 seconds
        try:
            return f()
        except ApiException as e:
            if e.status != 409:
                raise e
            time.sleep(1)
    return f()


def car_service_url():
    return 'https://%s%s' % (os.environ.get(APP_FQDN), os.environ.get(CAR_API_PATH))


def set_account_id(account_id = None):
    if not id or debug_mode():
        context().account_id = os.environ.get(CAR_TEST_ACCOUNT_ID).replace('_', '-').lower()
    else:
        context().account_id = account_id


def car_microservice_secret_name():
    return '%s-car-service-access-key' % context().account_id


def response_json(response):
    try:
        return response.json()
    except:
        return {}


def validate_car_service_access(key, passwd):
    if debug_mode():
        return True
    from secrets import encode
    encoded = encode('%s:%s' % (key, passwd))
    headers = {'Authorization': 'Basic %s' % encoded, 'Content-Type': 'application/json'}
    url = 'https://%s%s/health' % (os.environ.get(APP_FQDN), os.environ.get(CAR_API_PATH))
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        context().logger.warning('Status code when validating CAR service access: %d' % resp.status_code)
    return resp.status_code != 401


def generate_api_key():
    if debug_mode():
        return 'test-key', 'test-passwd'
    url = os.environ.get(API_KEY_GENERATION_URL)
    headers = {'Authorization': request.headers.get('Authorization'), 'Content-Type': 'application/json'}
    id = car_microservice_secret_name()
    resp = requests.post(url, data=json.dumps({'id': id}), headers=headers)
    data = response_json(resp)
    if resp.status_code != 200:
        raise Exception('API Key generation failed: %d, %s' % (resp.status_code, json.dumps(data)))
    return data['key'], data['passwd']


def get_resource(fname):
    resource_dir = join(split(dirname(realpath(__file__)))[0], RESOURCES)
    return join(resource_dir, fname)


def running_in_cluster():
    print ("show me KUBERNETES_SERVICE_HOST:")
    print (os.environ.get('KUBERNETES_SERVICE_HOST'))
    print ("show me KUBERNETES_SERVICE_HOST:")
    print (os.environ['KUBERNETES_SERVICE_HOST'])
    # print (os.environ)
    return os.environ.get('KUBERNETES_SERVICE_HOST') and True or False


def current_namespace():
    if running_in_cluster():
        with open('/var/run/secrets/kubernetes.io/serviceaccount/namespace') as f:
            return f.read().strip()
    else:
        return os.environ.get(DEBUG_NAMESPACE) or 'cp4s'


def cron_job_id(name):
    return 'cp4s-car-' + name


def secret_id(name):
    return f'{context().account_id}-{cron_job_id(name)}-secrets'


# def get_public_key():
#     if running_in_cluster():
#         key_file = DEFAULT_JWT_PUBLIC_KEY
#         print ("are we coming here for cluster?")
#         print (key_file)
#     else:
#         key_file = os.environ.get(DEBUG_PUBLIC_KEY, DEFAULT_JWT_PUBLIC_KEY)
#         print ("are we coming here for local environment?")
#     with open(key_file, 'rb') as file:
#         return jwk_from_pem(file.read())


def debug_mode():
    if os.getenv('JUNIT_MODE'):
        return False
    return os.getenv('DEBUG_MODE') and True or False
