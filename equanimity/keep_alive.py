import subprocess, time
#hackity hackity
a = subprocess.check_output(["which", "ipython"]).rstrip("\n")
cmd = [a, "equanimity/battle_server.py", '(0, 0)']
while True: subprocess.call(cmd)
