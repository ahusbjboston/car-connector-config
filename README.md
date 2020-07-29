# Introduction

CAR Connector Config Service provide Rest API to manage data sources (CAR Connectors) as a Cronjob of Kubernetes. 

# Connector Config API endpoints

These endpoints are to create the Cronjob for car connectors


### `/api/car-connector-config/v1/connectorConfigs`
Role: User

The GET request to list all of name of data sources  config (CAR Connectors config)

```
curl -X GET \ 
'<Path of the API>/api/car-connector-config/v1/connectorConfigs' \ 
-H 'Cache-Control: no-cache' \ 
-H 'Authorization: Basic eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImE2N2E0Nzg0In0' 

```
Response:

* Content
	
```
{ [ The string list of data sources ] }
```
* Status

```
200 
```
* Error

```
401 : Authentication error
```
### `/api/car-connector-config/v1/connectorConfigs`

Role: Admin

The Post request to upset the data source as a cronJob of K8s.

```
curl -X POST \ 
'<Path of the API>/api/car/v2/importstatus/{id}' \ 
-H 'Cache-Control: no-cache' \ 
-H 'Authorization: Basic eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImE2N2E0Nzg0In0'  \
--data {
    'connector_config': {
        'name': 'config1',
        'image": "connector:Rel_1',
        'frequency': ,
        'time': '12:20',
        'env_vars': {
           [
             'var1': 'value1',
             'var2': 'value2'
           ]
        },
        "secret_env_vars": {
           [
             'sec_var1': 'sec_value1',
             'sec_var2': 'sec_value2'
           ]
        }
    }
}
```

Response:

* Status

```
201 
```
* Error

```
401 : Authentication error
```

### `/api/car-connector-config/v1/connectorConfigs/{configName}`
Role: User

The Delete request to delete a specific  configuration of data sources(Car Connnector) from K8s

```
curl -X GET \ 
'<Path of the API>/api/car-connector-config/v1/connectorConfigs/{configName}' \ 
-H 'Cache-Control: no-cache' \ 
-H 'Authorization: Basic eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImE2N2E0Nzg0In0' 
```
Response:

* Content

```
{
    'connector_config': {
        'name': 'config1',
        'image": "connector:Rel_1',
        'frequency': ,
        'time': '12:20',
        'env_vars': {
           [
             'var1': 'value1',
             'var2': 'value2'
           ]
        },
        "secret_env_vars": {
           [
             'sec_var1': 'sec_value1',
             'sec_var2': 'sec_value2'
           ]
        }
    }
}
```

* Status

```
200 
```
* Error

```
401 : Authentication error
```


### `/api/car-connector-config/v1/connectorConfigs/{configName}`
Role: Admin

The GET request to get database status for account of which the apikey is provided.
```
curl -X DELETE \ 
'<Path of the API>/api/car-connector-config/v1/connectorConfigs/{configName}' \ 
-H 'Cache-Control: no-cache' \ 
-H 'Authorization: Basic eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImE2N2E0Nzg0In0' \ 
```
Response:
Response:

* Status

```
201 
```
* Error

```
401 : Authentication error
404 : Config does not exist
```



# Connector Config Schema


## Schema
```
{  
    "connector_config": {
	    "type": "object",
	    "properties": {
	        "name": {
	            "type": "string",
	            "format": "string"
	        },
	        "image": {
	            "type": "string",
	            "format": "string"
	        },
	        "frequency": {
	            "type": "integer",
	            "format": "int64"
	        },
	        "time": {
	            "type": "string",
	            "format": "date-time"
	        },
	        "env_vars": {
	            "type": "object",
	            "additionalProperties": {
                    "type": "string"
                }	        
           },
	        "secret_env_vars": {
	            "type": "object",
	            "additionalProperties": {
                    "type": "string"
                }
	        }
	    },
	    "required": [
	        "name",
	        "image"
	    ]
	}
} 
```

