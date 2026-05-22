import http.client
import json

conn = http.client.HTTPConnection('127.0.0.1', 8000, timeout=5)
conn.request('GET', '/health')
resp = conn.getresponse()
body = resp.read().decode()
print(resp.status, resp.reason)
print(body)
conn.close()
