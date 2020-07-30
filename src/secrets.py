import json, base64
from kubernetes import client, config
from kubernetes.client.rest import ApiException

from util import current_namespace, car_microservice_secret_name, generate_api_key, validate_car_service_access, ignore_404, handle_409
from context import context

CAR_SERVICE_API_KEY = 'key'
CAR_SERVICE_API_PASSWORD = 'passwd'


def encode(s):
    return base64.b64encode(s.encode()).decode()


def decode(s):
    return base64.b64decode(s).decode()


def create_car_microservice_access_secret():
    core_v1 = client.CoreV1Api(client.api_client.ApiClient())
    
    name = car_microservice_secret_name()
    print ("update1")
    print (name)

    data = ignore_404(lambda: core_v1.read_namespaced_secret(name, current_namespace()).data)
    if data:
        key, passwd = decode(data['key']), decode(data['passwd'])
        if validate_car_service_access(key, passwd):
            context().logger.info('API Key for CAR service access is validated.')
            return
        else:
            context().logger.info('API Key for CAR service access is not valid.')


    key, passwd = generate_api_key()
    data = {CAR_SERVICE_API_KEY: key, CAR_SERVICE_API_PASSWORD: passwd}
    create_secret(name, data)


def create_secret(name, data):
    core_v1 = client.CoreV1Api(client.api_client.ApiClient())
    ignore_404(lambda: core_v1.delete_namespaced_secret(name, current_namespace()))

    if not data:
        return

    context().logger.info('Creating secret %s for account %s' % (name, context().account_id))
    encoded_data = {}
    for k, v in data.items():
        encoded_data[k] = encode(v)
    metadata = {'name': name, 'namespace': current_namespace()}
    body = client.V1Secret(api_version='v1', data=encoded_data, kind='Secret', metadata=metadata, type='Opaque')
    handle_409(lambda: core_v1.create_namespaced_secret(current_namespace(), body))
