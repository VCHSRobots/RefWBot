# ldtst.py -- experiment with loading modules on the fly...

import os
import imports

flst = os.listdir()
print("Files Found: %d" % len(flst))
for f in flst:
    if f.endswith(".py") and f.startswith("robot_"):
        print(f)

imports.load