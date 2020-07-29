import os, sys, unittest, datetime

test_dir = os.path.dirname(os.path.realpath(__file__))
code_dir = os.path.split(test_dir)[0] + '/src'
sys.path.insert(0, test_dir)
sys.path.insert(0, code_dir)

from test_persister import TestPersister
from test_restapi import TestRestAPI
from connector_config import ConnectorConfig, SecretKeyRef
from template import Template
from context import Context

from test_cronjob_persister import CronjobPersisterTest
from test_cron_schedule import CronJobScheduleTest
class Test(unittest.TestCase):
    
    def test_persister(self):
        config1 = ConnectorConfig()
        config1.name = 'config1'
        config1.image = 'image1'
        config1.image_version = 'v112'
        config1.frequency = 30
        config1.env_vars = {'NAME1': 'VAL1', 'NAME2': 'VAL2', 'NAME3': 'VAL3'}

        config2 = ConnectorConfig()
        config2.name = 'config2'
        config2.image = 'image2'
        config2.image_version = 'v112'
        config2.frequency = 15
        config2.env_vars = {'NAME1': 'VAL1', 'NAME2': 'VAL2', 'NAME3': 'VAL3'}
        config2.secret_env_vars = {'SECRET_KEY1':'SECRET_VALUE1', 'SECRET_KEY2':'SECRET_VALUE2'}

        context = Context()
        context.account_id = 'test-account'
        pers = TestPersister()
        pers.upsert(config1)
        pers.upsert(config2)
        res = pers.list()
        self.assertEqual(len(res), 2)
        self.assertTrue('config1' in res)
        self.assertTrue('config2' in res)

        config = pers.get('config1')
        self.assertEqual('VAL1', config.env_vars['NAME1'])
        self.assertFalse(bool(config.secret_env_vars))

        config = pers.get('config2')
        self.assertEqual('VAL2', config.env_vars['NAME2'])
        self.assertEqual('SECRET_VALUE1', config.secret_env_vars['SECRET_KEY1'])

    def test_template_filler(self):
        config1 = ConnectorConfig()
        config1.name = 'config1'
        config1.image = 'image1'
        config1.image_version = 'v112'
        config1.frequency = 15
        config1.env_vars = {'NAME1': 'VAL1', 'NAME2': 'VAL2', 'NAME3': 'VAL3'}
        config1.secret_env_vars = {'SECRET_KEY1':'SECRET_VALUE1', 'SECRET_KEY2':'SECRET_VALUE2'}

        yaml_doc = Template().fill(config1)
        print(yaml_doc)


if __name__ == '__main__':
    os.environ['JUNIT_MODE'] = 'TRUE'
    unittest.TestLoader().sortTestMethodsUsing = None
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(Test))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(CronjobPersisterTest)) 
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(CronJobScheduleTest))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestRestAPI))

    unittest.TextTestRunner(verbosity=2).run(suite)
