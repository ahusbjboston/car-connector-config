import os, sys, unittest, datetime
from os.path import dirname, split, join, realpath

import secrets
secrets.create_car_microservice_access_secret = lambda: None

from connector_config import ConnectorConfig, SecretKeyRef
from cronjob_persister import CronJobPersister
from util import DEBUG_NAMESPACE, secret_id
from context import Context

class CronjobPersisterTest(unittest.TestCase):
    
    def test_cronjob_persister(self):
        os.environ[DEBUG_NAMESPACE] = 'unit-test'

        config1 = ConnectorConfig()
        config1.name = 'config1'
        config1.image = 'image1:v112'
        config1.frequency = 30
        config1.env_vars = {'NAME1': 'VAL1', 'NAME2': 'VAL2', 'NAME3': 'VAL3'}
        config1.secret_env_vars = {}

        config2 = ConnectorConfig()
        config2.name = 'config2'
        config2.image = 'image2:v114'
        config2.frequency = 15
        config2.env_vars = {'NAME1': 'VAL1', 'NAME2': 'VAL2', 'NAME3': 'VAL3'}
        config2.secret_env_vars = {'SECRET_KEY1': 'SECRET_VALUE1', 'SECRET_KEY2': 'SECRET_VALUE2'}

        kube_config = join(dirname(realpath(__file__)), 'config')

        context = Context(kube_config = kube_config)
        context.account_id = 'test-account'
        pers = CronJobPersister()
        context.persister = pers
        for name in pers.list():
            pers.delete(name)

        pers.upsert(config1)
        pers.upsert(config2)
        res = pers.list()
        self.assertEqual(2, len(res))
        self.assertTrue('config1' in res)
        self.assertTrue('config2' in res)

        config = pers.get('config1')
        self.assertEqual('config1', config.name)
        self.assertEqual('image1:v112', config.image)
        self.assertEqual(4, len(config.env_vars))
        self.assertEqual('VAL1', config.env_vars['NAME1'])
        self.assertEqual('VAL2', config.env_vars['NAME2'])
        self.assertEqual('VAL3', config.env_vars['NAME3'])
        self.assertEqual(0, len(config.secret_env_vars))
    
        config = pers.get('config2')
        self.assertEqual('config2', config.name)
        self.assertEqual('image2:v114', config.image)
        self.assertEqual(4, len(config.env_vars))
        self.assertEqual('VAL1', config.env_vars['NAME1'])
        self.assertEqual('VAL2', config.env_vars['NAME2'])
        self.assertEqual('VAL3', config.env_vars['NAME3'])
        self.assertEqual(2, len(config.secret_env_vars))
        self.assertEqual('SECRET_VALUE1', config.secret_env_vars['SECRET_KEY1'])
        self.assertEqual('SECRET_VALUE2', config.secret_env_vars['SECRET_KEY2'])

        pers.delete('config1')
        pers.delete('config2')
