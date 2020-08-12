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
    ## return context account_id here 
    print ("name for create_car_microservice_access_secret")
    print (name)

    data = ignore_404(lambda: core_v1.read_namespaced_secret(name, current_namespace()).data)
    print ("show me current name space secret data for car microservice secret")
    print (data)
    if data:
        key, passwd = decode(data['key']), decode(data['passwd'])
        if validate_car_service_access(key, passwd):
            print ("pass for validate")
            context().logger.info('API Key for CAR service access is validated.')
            return
        else:
            print ("failed for validate")
            context().logger.info('API Key for CAR service access is not valid.')


    # key, passwd = generate_api_key()
    data = {CAR_SERVICE_API_KEY: key, CAR_SERVICE_API_PASSWORD: passwd}
    print ("show me data for secret:")
    print (data)
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
    print ("show me encoded data")   
    print (encoded_data) 
    
    metadata = {'name': name, 'namespace': current_namespace()}
    print ("come here for create_secret ")
    # {'name': 'TNT_HMIYKXUFCW56WCEH2H9D38-cp4s-car-tan1-secrets', 'namespace': 'staging'}
    print (metadata)
    body = client.V1Secret(api_version='v1', data=encoded_data, kind='Secret', metadata=metadata, type='Opaque')
    handle_409(lambda: core_v1.create_namespaced_secret(current_namespace(), body))


def  read_secret():
    core_v1 = client.CoreV1Api(client.api_client.ApiClient())
    # secret = core_v1.read_namespaced_secret("insights-tenant-user-secret", "staging").data
    print ("show me current namespace")
    print (current_namespace())
    sec = core_v1.read_namespaced_secret("insights-tenant-user-secret", current_namespace()).data
    print (sec)
    #https://kubernetes.io/docs/tasks/inject-data-application/distribute-credentials-secure/#create-a-pod-that-has-access-to-the-secret-data-through-environment-variables
    pas=sec["_TENANT_USER_SECRET"]
    # print(pas)
    return pas


