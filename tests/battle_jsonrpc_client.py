import json, urllib

def request(url, func, *args):
    req = json.dumps({"method":func, "params":args, "id":1})
    result = urllib.urlopen(url, req).read()
    try:
        response = json.loads(result)
    except:
        return "error: %s" % result
    else:
        return response.get("result", response.get("error"))
"""
url = "http://localhost:8888/jsonrpc"
print "echo:", request(url, "echo", "foo bar")
print "sort:", request(url, "sort", ["foo", "bar"])
print "count:", request(url, "count", ["foo", "bar"])
print "geoip_lookup:", request(url, "geoip_lookup", "google.com")
"""

battle = "http://localhost:8888/battle"
q = request(battle, "get_states")
l = request("http://localhost:8888/jsonrpc/login", "login", {"u":"rix", "p":"xir"})
v = request(battle, "process_action", ['btl.squad1[0]', 'move', '(2,2)'])