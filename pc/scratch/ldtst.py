# ldtst.py -- experiment with loading modules on the fly...

import os
import sys

flst = os.listdir()
print("Files Found: %d" % len(flst))
module_file = ""
for f in flst:
    if f.endswith(".py") and f.startswith("robot_"):
        module_file = f

if module_file == "":
    print("User code not found!")
    sys.exit()
module_name = module_file[:-3]

print("Using File: %s" % module_name)
user_code = __import__(module_name)
user_code.HiThere()

