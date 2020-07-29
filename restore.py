#!/usr/bin/python

app = 'car-connector-config'

import os, sys, subprocess, re, json, time, uuid, urllib
from util import patch

old_isccomp = 'old-%s.yaml' % app
route_doc = '%s-debug-helper-route.yaml' % app

if not os.path.exists(old_isccomp) and not os.path.exists(route_doc):
    'Cannot restore: no data!'
    sys.exit(1)

if os.path.exists(old_isccomp):
    os.system('kubectl replace --force -f %s' % old_isccomp)
    patch('iscsequence', app, {'spec': {'labels': {'generation': '%s' % uuid.uuid1()}}})
    os.remove(old_isccomp)

if os.path.exists(route_doc):
    os.system('kubectl delete -f %s' % route_doc)
    os.remove(route_doc)
