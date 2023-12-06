import os

myfile = "instance/main.db"

if os.path.isfile(myfile):
  os.remove(myfile)
else:
  print(f"{myfile} does not exist")