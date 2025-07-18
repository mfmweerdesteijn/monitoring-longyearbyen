import requests
### Authentication

# Define the Tilsig API endpoint and credentials
endpoint = 'https://api.where2o.com/v1/authentication/authenticate'
username = 'maaikew@unis.no'
password = 'ToppTur1!2@3#4$'

# Define the data and headers for the token request
data = {
    'username': username,
    'password': password,
}

headers = {
   'accept': 'application/json',
   'Content-Type': 'application/json',
}

# Send the token request
r = requests.post(endpoint, json=data, headers=headers)

# Check if request succeeded and retrieve token
if r.status_code == 200:
    token_data = r.json()
    access_token = token_data['token']
else:
    print('Error! Returned status code %s' % r.status_code)