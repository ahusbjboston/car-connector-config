#!/usr/bin/python

app = 'car-connector-config'
files_to_push = ('.py', )

import os, subprocess, zipfile, re
from os.path import dirname, realpath, splitext, join

ocp_console = subprocess.check_output(['kubectl', 'get', '-n', 'openshift-console', '-o', 'jsonpath={..spec.host}', 'route', 'console'])
domain = re.sub('.*apps', 'apps', ocp_console)
debug_helper_url = '%s-debug-helper.%s' % (app, domain)
print('Pushing to: ' + debug_helper_url)

current_dir = os.getcwd()
os.chdir(join(dirname(dirname(realpath(__file__))), 'src'))
try:
    with open('files.zip', 'wb') as files_zip:
        zip = zipfile.ZipFile(files_zip, 'w')
        for root, folder, files in os.walk('.'):
            for file in files:
                if splitext(file)[1] in files_to_push:
                    zip.write(file)
        zip.close()

    os.system('curl -F "data=@files.zip" http://%s' % debug_helper_url)

finally:
    try: os.remove('files.zip')
    except: pass
    os.chdir(current_dir)
