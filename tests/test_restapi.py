import os, sys, unittest, jsonpickle
from flask import Flask

import entitlement
entitlement.entitlementCheck = lambda token, payload, required_access_level: None

import util
import api_v1
from test_persister import TestPersister
from connector_config import ConnectorConfig, SecretKeyRef
from context import Context
from jwt import JWT, jwk_from_pem
import datetime

test_dir = os.path.dirname(os.path.realpath(__file__))

token={
    'sub': "51WP7777",
    'isc_account': 	"0001",
    'isc_at': 	"ui1111111", 
    'iss':	"isc-dev.ite2.idng.example.com",
    'iat': 	1537342652,
    'exp':	1537349851,
    'email*': "scott-isc@cse-bank.net",
    'family_name*': "Damon",
    'given_name*':	"Scott",
    'apikey': '111111111a11111'
}

class TestRestAPI(unittest.TestCase):
    def get_header(self):
        with open(f'{test_dir}/test_jwt_privatekey.pem', 'rb') as fh:
           private_key = jwk_from_pem(fh.read())
        header = JWT().encode(token, private_key, 'RS256')
        header = {"Authorization" : f" Bearer {header}"}
        return header

    def expired_request(self):
        token['exp'] = int((datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%s'))
        header = self.get_header()
        result = self.client.get('/api/v1/connectorConfigs',
                headers=header)
        self.assertEqual(result.status_code, 401)
    

    def create_config(self, suffix):
        source_config = ConnectorConfig()
        source_config.name = 'config%s' % suffix
        source_config.image = 'image1:v11%s' % suffix
        source_config.frequency = 30
        source_config.env_vars = {'NAME1': 'VAL1', 'NAME2': 'VAL2', 'NAME3': 'VAL3'}
        source_config.secret_based_env_vars = {}
        result = self.client.post('/api/v1/connectorConfigs', 
            data=jsonpickle.encode(source_config),
            content_type='application/json',
            headers=self.header) 
        self.assertEqual(result.status_code, 201)

    def get_config(self, suffix):
        result = self.client.get('/api/v1/connectorConfigs/config%s' % suffix,
            headers=self.header)
        self.assertEqual(result.status_code, 200) 
        config = ConnectorConfig(jsonpickle.decode(result.data))
        self.assertEqual(config.name, 'config%s' % suffix)
        self.assertEqual(config.image, 'image1:v11%s' % suffix)
        self.assertEqual('VAL1', config.env_vars['NAME1'])
        return config

    def delete_config(self, name):
        result = self.client.delete(f'/api/v1/connectorConfigs/{name}',
            headers=self.header)
        self.assertEqual(result.status_code, 200)
        return result
    
    def get_allconfigs(self):
        result = self.client.get('/api/v1/connectorConfigs',
                headers=self.header)
        self.assertEqual(result.status_code, 200)
        return result

    def test_restapi(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(api_v1.api, url_prefix='/api/v1')
        context = Context()
        context.persister = TestPersister()
        self.client = self.app.test_client()
        self.client.testing = True 
        os.environ[util.DEBUG_PUBLIC_KEY] = f"{test_dir}/test_jwt_publickey.pem"
        token["iat"] = int(datetime.datetime.now().strftime('%s'));
        token['exp'] = int((datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%s'))
        self.header = self.get_header()


        # cleanup
        res = self.get_allconfigs()
        for name in jsonpickle.decode(res.data):
            self. delete_config(name)

        # create

        self.create_config("1")
        self.create_config("2")
        self.create_config("3")
        self.create_config("4")

        # list

        result = self.get_allconfigs() 
        self.assertEqual(result.status_code, 200)
        list = jsonpickle.decode(result.data)
        self.assertEqual(4, len(list))
        self.assertEqual(list.count("config1"), 1)
        self.assertEqual(list.count("config2"), 1)
        self.assertEqual(list.count("config3"), 1)
        self.assertEqual(list.count("config4"), 1)

        # get

        self.get_config("1")
        self.get_config("2")
        self.get_config("3")
        self.get_config("4")

        # update
        config = self.get_config("1")
        self.assertEqual(30, config.frequency)
        config.frequency = 40
        result = self.client.post('/api/v1/connectorConfigs/config1',
            data=jsonpickle.encode(config),
            content_type='application/json',
            headers=self.header) 
        config = self.get_config("1")
        self.assertEqual(40, config.frequency)

        # delete
        
        result = self.delete_config("config1")
        self.assertEqual(result.status_code, 200)
        result = self.delete_config("config2")
        self.assertEqual(result.status_code, 200)
        result = self.delete_config("config3")
        self.assertEqual(result.status_code, 200)
        result = self.delete_config("config4")
        self.assertEqual(result.status_code, 200)

        result = self.get_allconfigs()
        self.assertEqual(result.status_code, 200)
        list = jsonpickle.decode(result.data)
        self.assertEqual(0, len(list))

        #check jmt expired
        self.expired_request()


    @classmethod
    def tearDownClass(cls):
        os.environ.pop(util.DEBUG_PUBLIC_KEY)