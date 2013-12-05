import sys, random, os, time
from math import *

def get_energy(f):
  if not os.path.exists(f): return 0
  ret = 0
  f0 = open(f)
  for l in f0.readlines():
    if l.lstrip().startswith("Energy:"): ret += 1
  return ret
    
def get_struc(f):  
  if not os.path.exists(f): return 0
  ret = 0
  f0 = open(f)
  for l in f0.readlines()[-100:]:
    if not l.startswith("#"): continue
    try:
      v = int(l[1:])
    except ValueError:
      continue
    if v > ret: ret = v  
  f0.close()
  return ret

def finished(f, nstruc):
  if scoremode:
    fstruc = get_energy(f)
  else:
    fstruc = get_struc(f)
  return fstruc == nstruc

def run(command):
  print command
  os.system(command)  

np = 1
output = None
anr = 0
torque = ""
jobsize = None
strucs = None
while 1:
  anr += 1

  if anr > len(sys.argv)-1: break  
  arg = sys.argv[anr]
  if arg == "--torque":
    torque = "-torque"
    sys.argv = sys.argv[:anr] + sys.argv[anr+1:]
    anr -= 1
    continue
    
  if anr >= len(sys.argv)-1: break
  arg, nextarg = sys.argv[anr],sys.argv[anr+1]

  if arg == "-np" or arg == "--np":
    try:
      np = int(nextarg)
      if np <= 0: raise ValueError
    except ValueError: 
      raise ValueError("Invalid number of processors: %s" % nextarg)
    sys.argv = sys.argv[:anr] + sys.argv[anr+2:]
    anr -= 1
    continue
  if arg == "-jobsize" or arg == "--jobsize":
    try:
      jobsize = int(nextarg)
      if jobsize <= 0: raise ValueError
    except ValueError: 
      raise ValueError("Invalid jobsize: %s" % nextarg)
    sys.argv = sys.argv[:anr] + sys.argv[anr+2:]
    anr -= 1
    continue
  if arg == "-strucs" or arg == "--strucs" or arg == "-struc" or arg == "--struc":
    try:
      strucs = int(nextarg)
      if strucs <= 0: raise ValueError
    except ValueError: 
      raise ValueError("Invalid strucs: %s" % nextarg)
    sys.argv = sys.argv[:anr] + sys.argv[anr+2:]
    anr -= 1
    continue
  if arg == "--output":
    output = nextarg
    sys.argv = sys.argv[:anr] + sys.argv[anr+2:]
    anr -= 1

if output is None:
  raise ValueError("You must specify an output file with --output")

queue = [None for n in range(np)]

attractdir0 = os.path.split(sys.argv[0])[0]
tooldir = attractdir0 + "/../tools"
attractdir = attractdir0 + "/../bin"

attract = attractdir + "/attract" + torque
strucgen = sys.argv[1]

if jobsize is None:
  raise ValueError("You must specify --jobsize <value>")
if strucs is None:
  raise ValueError("You must specify --strucs <value>")

args = sys.argv[2:]
scoremode = "--score" in args
while 1:
  pat = "tmp%d" % random.randint(1,99999)
  if os.path.exists("%s-1" % pat): continue
  break  

try:
  done = 0
  current = 1
  while 1:
    for vnr in range(np):
      v = queue[vnr]
      if v is None: continue
      if finished(v, 1):         
	done += 1
	if done == strucs: break
	queue[vnr] = None
    if done == strucs: break

    free = [n for n,v in enumerate(queue) if v is None]
    if len(free) == 0 or current == strucs+1:
      time.sleep(0.5)
      continue

    q = free[0]
    outp = "%s-%d" % (pat, current)
    queue[q] = outp
    com = " ".join([strucgen + " %d |" % jobsize, attract, "/dev/stdin"]+args)
    com2 = "python %s/../tools/sort.py /dev/stdin | %s/../tools/top /dev/stdin 1 | sed 's/^#1$/#1\\n### SPLIT %d/' > %s-%d" % (attractdir0, attractdir0,  current, pat,  current)
    run(com + "|" + com2 + "&")
    current += 1

  o = open(output, "w")
  print >> o, "## Command line arguments: " + " ".join([attract,"<%s %d>" % (strucgen,jobsize)]+args)
  o.close()
  score = ""
  if scoremode:
    score = "--score"  
  com = "python %s/join.py %s %s >> %s" % (tooldir, pat, score, output) 
  run(com)
finally:
  com = "rm %s-*" % pat; run(com)