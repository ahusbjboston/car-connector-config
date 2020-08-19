from flask import request, Blueprint, Response
import entitlement, jsonpickle
from jwtcheker import requires_auth
from connector_config import ConnectorConfig

from errors import error_handler
from context import context


api = Blueprint('route', __name__)


@api.route('/connectorConfigs',  methods=['GET'])
@error_handler
@requires_auth(required_access_level=entitlement.readOnlyAccess)
def list():
    res = context().persister.list()
    return Response(jsonpickle.encode(res, unpicklable=False), status=200, mimetype='application/json')


@api.route('/connectorConfigs/<cronJobName>', methods=['GET']) 
@error_handler
@requires_auth(required_access_level=entitlement.readOnlyAccess)
def get(cronJobName):
    cronjob = context().persister.get(cronJobName)
    return Response(jsonpickle.encode(cronjob, unpicklable=False), status=200, mimetype='application/json')


@api.route('/connectorConfigs', methods=['POST'])
@error_handler
#@requires_auth(required_access_level=entitlement.readWriteAccess)
def create():
    print ("come to create")
    print (request.get_json())
    cronjob = context().persister.upsert(ConnectorConfig(request.get_json()))
    return Response(jsonpickle.encode(cronjob, unpicklable=False), status=201, mimetype='application/json')


@api.route('/connectorConfigs/<cronJobName>', methods=['POST'])
@error_handler
@requires_auth(required_access_level=entitlement.readWriteAccess)
def update(cronJobName):
    json_data = request.get_json()
    if json_data.get('name') != cronJobName:
        raise ValueError('Cron Job name mismatch.')
    cronjob = context().persister.upsert(ConnectorConfig(json_data=json_data))
    return Response(jsonpickle.encode(cronjob, unpicklable=False), status=200, mimetype='application/json')
      

@api.route('/connectorConfigs/<cronJobName>', methods=['DELETE'])
@error_handler
# @requires_auth(required_access_level=entitlement.readWriteAccess)
def delete(cronJobName):
    context().persister.delete(cronJobName)
    return Response('Success', 200, {'Content-Type': 'text/plain'})
