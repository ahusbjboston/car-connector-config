import os, json

def patch(type, name, data):
    json_data = json.dumps(data)
    command = "kubectl patch %s %s --type merge --patch '%s'" % (type, name, json_data)
    print(command)
    os.system(command)
