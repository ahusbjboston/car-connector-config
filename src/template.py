import yaml, re
from util import get_resource, cron_job_id
from cronjob_schedule import CronJobSchedule

class Template(object):

    def fill(self, car_config):
        self.post_processing = []
        self.car_config = car_config
        template = self._load_template()
        self._handle_value(template, None, None)
        for action in self.post_processing:
            print (action)
            action()
        return template
    

    def template_validate(self, car_config, template_file):
        if not car_config.secret_env_vars and self.template_file == 'secret_template.yaml':
            return False
        return True


    def env_vars(self):
        template = self._load_template()
        res = [item['name'] for item in template['spec']['jobTemplate']['spec']['template']['spec']['containers'][0]['env'] if type(item) == dict]
        return res


    def _load_template(self):
        with open(get_resource('template.yaml')) as f:
            yaml_document_all = yaml.safe_load_all(f)
            for yaml_document in yaml_document_all:
                return yaml_document


    def _generate_env_vars(self, container):
        for k, v in self.car_config.all_env_vars().items():
            print (k)
            print (v)
            container.append({'name': k, 'value': v})
        for k, v in self.car_config.secret_refs().items():
            print (k)
            print (v)
            container.append({'name': k, 'valueFrom': {'secretKeyRef': {'name': v.name, 'key': v.key}}})


    def _handle_value(self, value, parent, index):
        print (value)
        print (parent)
        print (index)
        if type(value) == dict:
            for key in value:
                self._handle_value(value[key], value, key)

        if type(value) == list:
            for index in range(len(value)):
                self._handle_value(value[index], value, index)

        if type(value) == str:
            m = re.search(r'{{(.+)}}', value)
            if m:
                var = m.group(1)
                if var == 'id': parent[index] = value.replace(m.group(0), cron_job_id(self.car_config.name))
                elif var == 'name': parent[index] = value.replace(m.group(0), self.car_config.name)
                elif var == 'image': parent[index] = value.replace(m.group(0), self.car_config.image)
                elif var == 'schedule': parent[index] = value.replace(m.group(0), CronJobSchedule(self.car_config).frequency_to_schedule())
                elif var == 'env_vars':
                    self.post_processing.append(lambda: parent.pop(index))
                    print (parent)
                    self._generate_env_vars(parent)
                else:
                    raise ValueError('Unknown varialble in the template: ' + m.group(0))