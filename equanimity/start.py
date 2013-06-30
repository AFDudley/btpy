import multiprocessing
import subprocess

def work(cmd):
    while True: subprocess.call(cmd)

ip = subprocess.check_output(["which", "ipython"]).rstrip("\n")
runzeo = ["runzeo", "-C", "zeoWorld.conf"]
battle = [ip, "equanimity/battle_server.py", '(0, 0)']
auth   = [ip, "equanimity/auth_server.py"]
rproxy = [ip, "equanimity/rproxy_server.py", "127.0.0.1"]
cmds = [runzeo, battle, auth, rproxy]

for cmd in cmds:
    p = multiprocessing.Process(target=work, args=(cmd,))
    p.start()
    
