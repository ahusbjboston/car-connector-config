import os, jsonpickle, glob, json
from context import Persister
from connector_config import ConnectorConfig

code_dir = os.path.dirname(os.path.realpath(__file__))
test_dir = os.path.split(code_dir)[0] + '/tests'

class TestPersister(Persister):
    def list(self):
        files = glob.glob('%s/*.testdata' % test_dir)
        return [os.path.splitext(os.path.split(f)[1])[0] for f in files]

    def get(self, name):
        fname = '%s/%s.testdata' % (test_dir, name)
        with open(fname) as f:
            return ConnectorConfig(jsonpickle.decode(f.read()))

    def upsert(self, config):
        fname = '%s/%s.testdata' % (test_dir, config.name)
        with open(fname, 'w') as f:
            f.write(jsonpickle.encode(config, unpicklable=False))

    def delete(self, name):
        fname = '%s/%s.testdata' % (test_dir, name)
        os.unlink(fname)
