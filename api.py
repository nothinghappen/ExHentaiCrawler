import requests
import json
from config.conf import API_URL

#从api获取本子信息
def getDataFromApi(gidlist):
    requestBody = {
        'method': 'gdata',
        'gidlist': [],
        'namespace': 1
    }
    requestBody['gidlist'] = gidlist
    r = requests.post(API_URL,json=requestBody)
    return json.loads(r.text)