# ldtst.py -- experiment with loading modules on the fly...

import os

flst = os.listdir()
print("Files Found: %d" % len(flst))
for f in flst:
    print(f)
    if f.endswith(".py") and f.startswith("robot_"):
        print(f)
