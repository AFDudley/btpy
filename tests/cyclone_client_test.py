import json
import urllib
import httplib2

def request(url, func, *args):
    req = json.dumps({"method":func, "params":args, "id":1})
    result = urllib.urlopen(url, req).read()
    print req
    print result
    try:
        response = json.loads(result)
        print response
    except:
        return "error: %s" % result
    else:
        return response.get("result", response.get("error"))
        
battle = "http://localhost:8888/battle"
#g = request(battle, "get_state")
#l = request("http://localhost:8888/jsonrpc/login", "login", {"u":"rix", "p":"xir"})
#p = request(battle, "process_action", ['btl.squad1[0]', 'move', '(2,2)'])



http = httplib2.Http()

url = 'http://localhost:8888/auth/login'   
body = {'u': 'rix', 'p': 'xir'}
headers = {'Content-type': 'application/x-www-form-urlencoded'}
response, content = http.request(url, 'POST', headers=headers, body=urllib.urlencode(body))

headers = {'Cookie': response['set-cookie']}

url = 'http://localhost:8888/battle'
body = json.dumps({"method":"process_action", "params":[['btl.squad1[0]', 'move', '(2,2)']], "id":1})
response, content = http.request(url, 'POST', headers=headers, body=body)
