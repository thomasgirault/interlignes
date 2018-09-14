import json as js

try:
    VARS
except NameError:
    print("VARS is undefined")
    VARS = js.load(open("params.json", "r"))
    VARS["learnBG"] = 0

print(VARS)
