# ldtst.py -- experiment with loading modules on the fly...

import os
import sys

class Base():
    def __init__(self):
        pass
    def back_to_you(self):
        print("In back to you.")
ourplace = os.path.dirname(os.path.abspath(__file__))

print("Script directory: %s" % ourplace)
flst = os.listdir(ourplace)
print("Files Found: %d" % len(flst))
print("Files=", flst)
module_file = ""
for f in flst:
    if f.endswith(".py") and f.startswith("robot_"):
        module_file = f

if module_file == "":
    print("User code not found!")
    sys.exit()
module_name = module_file[:-3]

print("Using File: %s" % module_name)
user_module = __import__(module_name)
print("User Module = %s" % user_module)
user_class = getattr(user_module, "WaterBot")
base = Base()
user = user_class(base)
user.tryfunc()


