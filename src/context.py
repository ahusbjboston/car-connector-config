import threading, logging

class Persister(object):

    def list(self):
        pass

    def get(self, name):
        pass

    def upsert(self, config):
        pass    

    def delete(self, name):
        pass


def create_logger(debug = False):
    logger = logging.getLogger()
    logger.setLevel(debug and logging.DEBUG or logging.INFO)

    handler = logging.StreamHandler()
    handler.setLevel(debug and logging.DEBUG or logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


class Context(object):

    def __init__(self, kube_config=None):
        global global_context
        global_context = self

        self.logger = create_logger()
        self.persister = None
        self.kube_config = kube_config
        self.tls = threading.local()


    @property
    def account_id(self):
        return self.tls.account_id


    @account_id.setter
    def account_id(self, value):
        self.tls.account_id = value


global_context = None
def context():
    return global_context
