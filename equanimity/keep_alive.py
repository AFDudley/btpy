import subprocess, time
#hackity hackity
ip = subprocess.check_output(["which", "ipython"]).rstrip("\n")
cmd = [ip, "equanimity/battle_server.py", '(0, 0)']
while True: subprocess.call(cmd)
