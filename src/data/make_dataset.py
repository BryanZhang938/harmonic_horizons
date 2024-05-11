from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
import pandas as pd
import numpy as np

load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

def get_token():
    auth_string = f'{client_id}:{client_secret}'
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')

    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': f'Basic {auth_base64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type': 'client_credentials'}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result['access_token']
    return token

def get_auth_header(token):
    return {'Authorization': f'Bearer {token}'}

def search_for(token, search_query, *filters, limit = 10):
    headers  = get_auth_header(token)
    query_url = f'https://api.spotify.com/v1/search?q={search_query}&type={','.join(filters)}&limit={limit}'
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)

    if not json_result:
        return None
    
    return json_result

token = get_token()