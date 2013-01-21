import multiprocessing
import subprocess
#hackity hackity
def work(cmd):
    while True: subprocess.call(cmd)
ip = subprocess.check_output(["which", "ipython"]).rstrip("\n")
runzeo = ["runzeo", "-C", "zeoWorld.conf"]
#if I was a gangster, I'd use list comprehension here.
battle = [ip, "equanimity/battle_server.py", '(0, 0)']
auth   = [ip, "equanimity/auth_server.py"]
rproxy = [ip, "equanimity/rproxy_server.py", "127.0.0.1"]
cmds = [runzeo, battle, auth, rproxy]

"""while True:
    for cmd in cmds:
        subprocess.call(cmd)
"""
"""
ps =[]
pool = multiprocessing.Pool(processes=4)
for cmd in cmds:
    print cmd
    pool.apply_async(work(cmd))
"""
ps = []
for cmd in cmds:
    p = multiprocessing.Process(target=work, args=(cmd,))
    p.start()
    