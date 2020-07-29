import datetime, secrets

from template import Template
from util import secret_id
from cronjob_schedule import CronJobSchedule
from util import car_microservice_secret_name, car_service_url
from secrets import CAR_SERVICE_API_KEY, CAR_SERVICE_API_PASSWORD

CAR_SERVICE_URL = 'URL'
CAR_SERVICE_API_KEY_ENV_VAR = 'API_KEY'
CAR_SERVICE_API_PASSWORD_ENV_VAR = 'PASSWORD'


class SecretKeyRef(object):
    def __init__(self, name, key):
        self.name = name
        self.key = key


class ConnectorConfig(object):
    def __init__(self, json_data = None, cron_job = None, secret_env_vars = None):
        if json_data:
            self.name = json_data.get('name')
            self.image = json_data.get('image')
            
            self.frequency = json_data.get('frequency')
            self.time = json_data.get('time')

            self.env_vars = json_data.get('env_vars') or {}
            self.secret_env_vars = json_data.get('secret_env_vars') or {}

        if cron_job:
            self.name = cron_job.metadata.labels['name']
            self.image = cron_job.spec.job_template.spec.template.spec.containers[0].image
            schedule = cron_job.spec.schedule
            frequency, start_min, start_h = CronJobSchedule(self).schedule_to_frequency(schedule)
            if start_h:
                # It daily frequency
                self.time = '%02d:%02d' % (start_h, start_min)
            else: 
                # It is minute frequency
                self.time = None
            self.frequency = frequency
            self.env_vars, self.secret_env_vars  = {}, {}
            template_env_vars = Template().env_vars()
            for item in cron_job.spec.job_template.spec.template.spec.containers[0].env:
                name = item.name
                if name in template_env_vars: continue
                if name in (CAR_SERVICE_API_KEY_ENV_VAR, CAR_SERVICE_API_PASSWORD_ENV_VAR): continue
                value = item.value
                value_from = item.value_from
                if value: self.env_vars[name] = value
            if secret_env_vars: 
                for k, v in secret_env_vars.data.items():
                    self.secret_env_vars[k] = str(secrets.decode(v))

    def secret_refs(self):
        res = {}
        for k in self.secret_env_vars:
            res[k] = SecretKeyRef(secret_id(self.name), k)

        res[CAR_SERVICE_API_KEY_ENV_VAR] = SecretKeyRef(car_microservice_secret_name(), CAR_SERVICE_API_KEY)
        res[CAR_SERVICE_API_PASSWORD_ENV_VAR] = SecretKeyRef(car_microservice_secret_name(), CAR_SERVICE_API_PASSWORD)
        return res

    def all_env_vars(self):
        res = self.env_vars.copy()
        res[CAR_SERVICE_URL] = car_service_url()
        return res
