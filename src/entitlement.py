import requests, json, os, errors
from requests.exceptions import ContentDecodingError, Timeout, InvalidURL, ContentDecodingError

# readOnlyAccess = ('canUseDataConnections')
# readWriteAccess = ('canUseDataConnections', 'canCreateDataConnections')

# readOnlyAccess = ('permission:datasource:view')
# readWriteAccess = ('permission:datasource:view',"permission:datasource:create")

readOnlyAccess = ("permission:group:create",)
readWriteAccess = ("permission:group:create",)



def entitlementCheck(jwtToken, jwtdecodedToken, required_access_level):
    # body = {
    #     'userId': jwtdecodedToken['sub'],
    #     'accountId': jwtdecodedToken['isc_account'],
    #     'applicationId': 'UDS'
    # }

    # “exp” (Expiration Time) Claim
    # “nbf” (Not Before Time) Claim
    # “iss” (Issuer) Claim
    # “aud” (Audience) Claim
    # “iat” (Issued At) Claim

    # body = {
    #     'userId': jwtdecodedToken['details']['uid'],
    #     'tenantID': jwtdecodedToken['details']['tenantID'],
    #     'applicationId': 'tenantuser'
    # }

    entitlements_response= jwtdecodedToken['details']['userPrivileges']
    print (entitlements_response)
    print (required_access_level)
    print ("show me the readOnlyAccess")
    print (readOnlyAccess)
    if entitlements_response :
        for permission in required_access_level:
            try: 
                print (permission)
                entitlements_response.index(permission)
            except ValueError: raise errors.AuthError(f'Authorization faild: Blocking unauthorized access due to missing role {permission}', 401)
    else:
        raise errors.AuthError('Failed to get entitlements. Cannot get the entitlements.', 401)
            
    # try:
    #     response = requests.post(
    #         os.environ.get('ENTITLEMENTS_API') + '/application',
    #         headers = {
    #             'accept': 'application/json',
    #             'content-type': 'application/json',
    #             'Authorization': f'Bearer {jwtToken}'
    #             },
    #         timeout = 10000,
    #         json = True,
    #         data = json.dumps(body)
    #     )
    #     entitlements_response = response.json()
    #     if entitlements_response and entitlements_response['entitlements'][0]:
    #         for permission in required_access_level:
    #             try: entitlements_response['entitlements'][0]['permissions'].index(permission)
    #             except ValueError: raise errors.AuthError(f'Authorization faild: Blocking unauthorized access due to missing role {permission}', 401)
    #     else:
    #         raise errors.AuthError('Failed to get entitlements. Cannot get the entitlements.', 401)
            
    # except (ContentDecodingError, Timeout, InvalidURL, ContentDecodingError) as e:
    #     raise errors.AuthError(f'Failed to get entitlements.', 401)
