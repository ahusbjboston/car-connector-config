import requests, json, os, errors
from requests.exceptions import ContentDecodingError, Timeout, InvalidURL, ContentDecodingError

readOnlyAccess = ('canUseDataConnections',)
readWriteAccess = ('canUseDataConnections', 'canCreateDataConnections')

def entitlementCheck(jwtToken, jwtdecodedToken, required_access_level):
    body = {
        'userId': jwtdecodedToken['sub'],
        'accountId': jwtdecodedToken['isc_account'],
        'applicationId': 'UDS'
    }

    try:
        response = requests.post(
            os.environ.get('ENTITLEMENTS_API') + '/application',
            headers = {
                'accept': 'application/json',
                'content-type': 'application/json',
                'Authorization': f'Bearer {jwtToken}'
                },
            timeout = 10000,
            json = True,
            data = json.dumps(body)
        )
        entitlements_response = response.json()
        if entitlements_response and entitlements_response['entitlements'][0]:
            for permission in required_access_level:
                try: entitlements_response['entitlements'][0]['permissions'].index(permission)
                except ValueError: raise errors.AuthError(f'Authorization faild: Blocking unauthorized access due to missing role {permission}', 401)
        else:
            raise errors.AuthError('Failed to get entitlements. Cannot get the entitlements.', 401)
            
    except (ContentDecodingError, Timeout, InvalidURL, ContentDecodingError) as e:
        raise errors.AuthError(f'Failed to get entitlements.', 401)
