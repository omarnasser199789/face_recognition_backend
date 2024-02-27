import requests
import ssl

url = 'https://myybs.ybservice.com:6443/v2/checkStatus'
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
apiResponse = requests.get(url, verify=ssl_context)
