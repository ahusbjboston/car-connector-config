import datetime, time
from kubernetes import client, config
from kubernetes.utils.create_from_yaml import create_from_yaml_single_item
from kubernetes.client.rest import ApiException

from context import Persister, context
from template import Template
from secrets import create_car_microservice_access_secret, create_secret
from util import current_namespace, cron_job_id, running_in_cluster, secret_id, ignore_404, handle_409
from connector_config import ConnectorConfig, SecretKeyRef

class CronJobPersister(Persister):

    def __init__(self):
        if running_in_cluster():
            config.load_incluster_config()
        else:
            config.load_kube_config(config_file = context().kube_config)
        self.k8s_client = client.api_client.ApiClient()


    def upsert(self, car_config):
        print ("comme to upsert method")
        ignore_404(lambda: self.delete(car_config.name))

        create_car_microservice_access_secret()
        create_secret(secret_id(car_config.name), car_config.secret_env_vars)

        yaml_doc = Template().fill(car_config)
        handle_409(lambda: create_from_yaml_single_item(self.k8s_client, yaml_doc, verbose=True, namespace=current_namespace()))


    def get(self, name):
        batch_v1beta1 = client.BatchV1beta1Api()
        cron_job = batch_v1beta1.read_namespaced_cron_job(cron_job_id(name), current_namespace())
        secret = ignore_404(lambda: client.CoreV1Api().read_namespaced_secret(secret_id(name), current_namespace()))
        return ConnectorConfig(cron_job = cron_job, secret_env_vars = secret)


    def list(self):
        batch_v1beta1 = client.BatchV1beta1Api()
        cron_jobs = batch_v1beta1.list_namespaced_cron_job(current_namespace(), label_selector='type=carconnector')
        return [cron_job.metadata.labels['name'] for cron_job in cron_jobs.items]

    
    def delete(self, name):
        DELETE_OPTIONS = client.V1DeleteOptions( 
            propagation_policy = 'Foreground', 
            grace_period_seconds = 5 
        )
        ignore_404(lambda: client.CoreV1Api().delete_namespaced_secret(secret_id(name), current_namespace(), body = DELETE_OPTIONS))
        client.BatchV1beta1Api().delete_namespaced_cron_job(cron_job_id(name), current_namespace(), body = DELETE_OPTIONS)
