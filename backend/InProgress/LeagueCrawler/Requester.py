import os
import requests
import time

from typing import Any
from requests import RequestException

api_key = os.environ.get('RG-API-KEY')

def request(url: str) -> Any | None:
    response = None
    url = url + api_key

    try:
        response = requests.get(url=url)
    except RequestException:
        time.sleep((100/120)*4)
        request(url=url)

    if response.status_code != 200:
        print(f'* [ERROR] Response returned {response.status_code} - retrying...')
        print(f'* [ERROR] {response}')
        time.sleep((100/120)*4)
        request(url=url)
        return None
    else:
        time.sleep((120/100)*2)
        return response.json()
