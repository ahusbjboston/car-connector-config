import os, sys, unittest, datetime

test_dir = os.path.dirname(os.path.realpath(__file__))
code_dir = os.path.split(test_dir)[0] + '/src'
sys.path.insert(0, test_dir)
sys.path.insert(0, code_dir)

from connector_config import ConnectorConfig, SecretKeyRef
from cronjob_schedule import CronJobSchedule
from mock import mock

class CronJobScheduleTest(unittest.TestCase):
    MOCK_VALUE = 5
    def test_frequency_to_schedule(self):
        with mock.patch('random.randrange', return_value=self.MOCK_VALUE) as mock_random:
            config = ConnectorConfig()
            config.name = 'config'
            config.image = 'image1'
            config.image_version = 'v112'
            
            config.env_vars = {'NAME1': 'VAL1', 'NAME2': 'VAL2', 'NAME3': 'VAL3'}
            config.secret_based_env_vars = {'S1': SecretKeyRef('SECRET_NAME1', 'SECRET_KEY1'), 'S2': SecretKeyRef('SECRET_NAME2', 'SECRET_KEY2')}

            # schedule within an hour (every x minutes)
            config.frequency = 20
            config.time = None
            cron_schedule = CronJobSchedule(config).frequency_to_schedule()
            self.assertEqual(cron_schedule, '{},25,45 * * * *'.format(self.MOCK_VALUE))
            # schedule within a day (every x hours)
            config.frequency = 120
            config.time = None
            cron_schedule = CronJobSchedule(config).frequency_to_schedule()
            self.assertEqual(cron_schedule, '{} {},7,9,11,13,15,17,19,21,23,1,3 * * *'.format(self.MOCK_VALUE, self.MOCK_VALUE))
            # schedule daily wiht start_time (every day starting from start_time)
            config.frequency = 1440
            config.time = '23:05'
            cron_schedule = CronJobSchedule(config).frequency_to_schedule()
            self.assertEqual(cron_schedule, '05 23 * * *')
            # schedule daily without start_time (every day starting from random value)
            config.frequency = 1440
            config.time = None
            cron_schedule = CronJobSchedule(config).frequency_to_schedule()
            self.assertEqual(cron_schedule, '{} {} * * *'.format(self.MOCK_VALUE, self.MOCK_VALUE))

            # schedule with unpermitted frequency
            config.frequency = 45
            config.time = None
            # cron_schedule = CronJobSchedule(config).frequency_to_schedule()
            with self.assertRaises(ValueError): CronJobSchedule(config).frequency_to_schedule()
    
    def test_schedule_to_frequency(self):
        with mock.patch('random.randrange', return_value=self.MOCK_VALUE) as mock_random:
            config = ConnectorConfig()
            config.name = 'config'
            config.image = 'image1'
            config.image_version = 'v112'
            
            config.env_vars = {'NAME1': 'VAL1', 'NAME2': 'VAL2', 'NAME3': 'VAL3'}
            config.secret_based_env_vars = {'S1': SecretKeyRef('SECRET_NAME1', 'SECRET_KEY1'), 'S2': SecretKeyRef('SECRET_NAME2', 'SECRET_KEY2')}

            # schedule within an hour (every x minutes)
            config.frequency = 20
            config.time = None
            cron_schedule = CronJobSchedule(config).frequency_to_schedule()
            frequency, start_min, start_h = CronJobSchedule(config).schedule_to_frequency(cron_schedule)
            self.assertEqual(frequency, 20)
            self.assertEqual(start_min, None)
            self.assertEqual(start_h, None)

            # schedule within a day (every x hours)
            config.frequency = 120
            config.time = None
            cron_schedule = CronJobSchedule(config).frequency_to_schedule()
            frequency, start_min, start_h = CronJobSchedule(config).schedule_to_frequency(cron_schedule)
            self.assertEqual(frequency, 120)
            self.assertEqual(start_min, None)
            self.assertEqual(start_h, None)

            # schedule daily wiht start_time (every day starting from start_time)
            config.frequency = 1440
            config.time = '23:05'
            cron_schedule = CronJobSchedule(config).frequency_to_schedule()
            frequency, start_min, start_h = CronJobSchedule(config).schedule_to_frequency(cron_schedule)
            self.assertEqual(frequency, 1440)
            self.assertEqual(start_min, 5)
            self.assertEqual(start_h, 23)

            # schedule daily without start_time (every day starting from random value)
            config.frequency = 1440
            config.time = None
            cron_schedule = CronJobSchedule(config).frequency_to_schedule()
            frequency, start_min, start_h = CronJobSchedule(config).schedule_to_frequency(cron_schedule)
            self.assertEqual(frequency, 1440)
            self.assertEqual(start_min, self.MOCK_VALUE)
            self.assertEqual(start_h, self.MOCK_VALUE)
