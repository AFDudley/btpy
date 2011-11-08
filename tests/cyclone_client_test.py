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

class test_client():
    def __init__(self, addr='localhost:8888'):
        self.addr = addr
        self.cookie = None
        self.http = httplib2.Http()

    def signup(self, u, p):
        url = 'http://' + self.addr + '/signup'
        body = urllib.urlencode({'u': u, 'p': p})
	headers = {'Content-type': 'application/x-www-form-urlencoded'}
        return self.http.request(url, 'POST', headers=headers, body=body)
    
    def login(self, u, p):
        url = 'http://' + self.addr + '/auth/login'
        body = urllib.urlencode({'u': u, 'p': p})
	headers = {'Content-type': 'application/x-www-form-urlencoded'}
        return self.http.request(url, 'POST', headers=headers, body=body)

    def battle(self, method, params, cookie):
        url = 'http://' + self.addr + '/battle'
        body = json.dumps({"method": method, "params":params, "id":1})
	headers = {'Cookie': cookie}
	return self.http.request(url, 'POST', headers=headers, body=body)
    
    def test_move(self, cookie):
        params = [['btl.squad1[0]', 'move', '(2,2)']]
        return self.battle("process_action", params, cookie)

    def register(self, cookie):
        params = []
	return self.battle("register", params, cookie)
if __name__ == "__main__":
   
    t = test_client()
    cookie = t.login('rix', 'xir')[0]['set-cookie']
    #print t.test_move(cookie)
    print t.register(cookie)
