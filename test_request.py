import requests

url = 'https://myybs.ybservice.com:6443/v2/checkStatus'

apiResponse = requests.get(url , headers = {'User-agent': 'your bot 0.1'},verify=False)
print(apiResponse.status_code)
