#!/usr/bin/python

app = 'car-connector-config'

import os, sys, subprocess, re, json, time, uuid, urllib
from util import patch

def create_from_template(template, doc, **args):
    with open(template) as input:
        with open(doc, 'w') as output:
            contents = input.read()
            for k, v in args.items():
                contents = contents.replace('{%s}' % k, v)
            output.write(contents)
    os.system('kubectl create -f ' + doc)

old_isccomp = 'old-%s.yaml' % app
route_doc = '%s-debug-helper-route.yaml' % app

if os.path.exists(old_isccomp) or os.path.exists(route_doc):
    'Already prepared!'
    sys.exit(1)

namespace = subprocess.check_output(['kubectl', 'config', 'view', '--minify', '-o', 'jsonpath={..namespace}']).strip().decode()
print('current namespace: ' + namespace)

ocp_console = subprocess.check_output(['kubectl', 'get', '-n', 'openshift-console', '-o', 'jsonpath={..spec.host}', 'route', 'console'])
print('OCP console: ' + ocp_console)
domain = re.sub('.*apps', 'apps', ocp_console)
debug_helper_url = '%s-debug-helper.%s' % (app, domain)

os.system('kubectl get isccomponent %s -o yaml >%s' % (app, old_isccomp))

patch('isccomponent', app, {'spec': {'action': {'service': {'ports': [3200, 12424], 'proto': 'http'}, 'image': {'repository': 'gsturov/%s-with-debug-helper' % app, 'tag': 'latest'}}}})
patch('iscsequence', app, {'spec': {'labels': {'generation': '%s' % uuid.uuid1()}}})

while True:
    s = subprocess.check_output(['kubectl', 'get', 'deployment', app, '-o', 'yaml']).strip().decode()
    if 'gsturov' in s: break
    else: print('waiting for the deployment to get updated...'); time.sleep(2)

time.sleep(2)

create_from_template('debug-helper-route-template.yaml', route_doc, app = app, namespace = namespace, debug_helper_url = debug_helper_url)

while True:
    try: 
        status = urllib.urlopen('http://%s' % debug_helper_url).read()
        if 'GET' in status: break
    except: pass
    print('waiting for debug-helper to come up...')
    time.sleep(2)
