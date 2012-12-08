import sys
from equanimity_client import test_client
t = test_client(sys.argv[1])
print t.signup('atkr', 'atkr')
print t.signup('dfndr', 'dfndr')
