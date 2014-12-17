#This script recognize set of reflectors, and allows only according movement, while iterating it. 
#Written by Michael Simkin 2014
import golly as g 
import copy

data = []
data.append(["2o5b2o$2o5bo$5bobo$5b2o$b2o$bobo$2bo2$5b3o$5b3o$5b3o$8b3o$8b3o$8b3o!", "P8 Reflector"])
data.append(["22b2o$22bo$11b2o7bobo$11bobo6b2o$6b2o4b3o$5bo2bo4b3o$7bo4b3o$3bo7bobo$2bob2o5b2o$2bo$b2o!", "P30 Reflector", [(1, -1)]])
data.append(["13bo$11b3o$10bo$10b2o3$18b2ob2o$19bob2o$19bo$11b2o4b3o$11b2o3bo3b2o$16b4o2bo$2b2o15bob2o$bobo12b3o2bo$bo13bo5bo$2o14b5o$18bo!", "Snark1"])
data.append(["13bo$11b3o$10bo$10b2o3$18b2o$19bo$19bob2o$11b2o4b3o2bo$11b2o3bo3b2o$16b4o$2b2o15bo$bobo12b3o$bo13bo$2o14b5o$20bo$18bo$18b2o!", "Snark2"])

def FindPeriod(obj):
   evolved = g.evolve(obj, 1)
   
   for i in xrange(1, 1000):
      if str(evolved) == str(obj):
         return i
         
      evolved = g.evolve(evolved, 1)
   
   return -1
   
def GetSize(obj):
   maxX = -1
   maxY = -1
   minX = 1000
   minY = 1000
   
   for i in xrange(0, len(obj), 2):
      if obj[i] > maxX:
         maxX = obj[i]
      
      if obj[i + 1] > maxY:
         maxY = obj[i + 1]
      
      if obj[i] < minX:
         minX = obj[i]
      
      if obj[i + 1] < minY:
         minY = obj[i + 1]
   
   return (maxX - minX, maxY - minY)
   
def GetTransList():
   transList = []
   
   for i in xrange(-1, 2, 2):
      for j in xrange(-1, 2, 2):
         transList.append((i, 0, 0, j))
         transList.append((0, i, j, 0))
   
   return transList
   
def GetObjectClickArray(obj, objName, t, period):
      
   result = []
   
   
   for i in xrange(0, len(obj), 2):
      x = obj[i]
      y = obj[i + 1]
      
      l = copy.copy(obj)
      
      for j in xrange(0, len(obj), 2):
         l[j] -= x
         l[j + 1] -= y
         
      result.append([l, objName, t, period])
   
   return result
   

def GetObjectArray(iniobj):
   result = []
   transList = GetTransList()
   period = FindPeriod(iniobj[0])
   for i in xrange(0, period):
      
      obj = g.evolve(iniobj[0], i)
      
      for t in transList:
         dxx, dxy, dyx, dyy = t
         curobj = g.transform(obj, 0, 0, dxx, dxy, dyx, dyy)
         
         result.extend(GetObjectClickArray(curobj, iniobj[1], t, period))
      
   return result 
   
def IsObjectExists(objectArray, x, y):
   for obj, objName, t, p in objectArray:
      found = True
      
      for i in xrange(0, len(obj), 2):
         dx = obj[i]
         dy = obj[i + 1]
         
         if g.getcell(x + dx, y + dy) == 0:
            found = False
            break

      if found:
         return [obj, objName, x, y, t, p]
   
   return None
   
def GetObjectByClick(event):   
   
   x = int(event.split()[1])
   y = int(event.split()[2]) 
   
   found = False
   
   for i in [0, -1, 1, -2, 2]:
      for j in [0, -1, 1]:
         if found:
            break
            
         o =  IsObjectExists(objectArray, x + i, y + j)
         
         if o != None:
            g.show("found!")
            
            for k in xrange(0, len(o[0]), 2):
               dx = o[0][k]
               dy = o[0][k + 1]
               
               g.setcell(x + i + dx, y + j + dy, 0)
               
            found = True

            g.update()
            
            
   if    found:
      return o
   else :
      return None
      
def ClearRect(x, y, w, h):
   for i in xrange(0, w):
      for j in xrange(0, h):
         g.setcell(x + i, y + j, 0)

def GetDirection(t):
   dxx, dxy, dyx, dyy = t
   
   if dxy == 0:
      return dxx * dyy
   else:
      return dxy * dyx

def GetEvolveDirection(t):
   dxx, dxy, dyx, dyy = t
   
   if dxy == 0:
      return -dxx
   else:
      return -dxy 

def FinishMove(d, w, h, x0, y0, p, t):
	
   under = d[0]
   obj = d[1]
   x = d[2]
   y = d[3]
   
   if under != -1:
      g.putcells(under)
	  
   g.putcells(g.evolve(obj, p + GetEvolveDirection(t) * ((4 * (x - x0)) % p)), x, y)
   
   g.update()
   
def UpdateMove(d, w, h, x0, y0, p, t):
   
   under = d[0]
   obj = d[1]
   x = d[2]
   y = d[3]
   
   
   if under != -1:
      ClearRect(x - w, y - h, 2 * w + 1, 2 * h + 1)
      g.putcells(under)
   
   
   val = g.getxy()
   
   if val == "":
      return 
      
   
   x1 = int(val.split()[0])
   y1 = y0 + GetDirection(t) * (x1 - x0)
   
   d[0] = g.getcells([x1 - w, y1 - h, 2 * w + 1, 2 * h + 1])
   
   #ClearRect(x1 - w, y1 - h, 2 * w + 1, 2 * h + 1)
   
   g.putcells(g.evolve(obj, p + GetEvolveDirection(t) * ((4 * (x1 - x0)) % p)), x1, y1)
   
   g.update()
   
   d[2] = x1
   d[3] = y1
   
def InitUpdateMove(obj, x, y):
   return [-1, obj, x, y]
   
   
objectArray = []

for d in data:
   objectArray.extend(GetObjectArray([g.parse(d[0]), d[1]]))
   
moving = False
g.show("Select known object with left click, exit with right click")
handling = False
searching = False

while True:

   event = g.getevent()
   
   if handling or searching:
      continue 
      
   handling = True

   if "click" in event:
   
      if "right" in event:
         g.show("finish smart movement")
         
         g.exit()
         
      if not moving:
         searching = True
         g.show("searching...")
         g.update()
         
		 
         found = GetObjectByClick(event)
         if found != None:
            p = found[5]
            t = found[4]
            curMove = InitUpdateMove(found[0], found[2], found[3])
            g.show("Found: "  + str(found[1]) + ", click left to place and continue, right to place and exit")
            w, h = GetSize(found[0])
            moving = True
			
         searching = False
		 
      else:
         if "left" in event and not searching:
            moving = False
            FinishMove(curMove, w, h, found[2], found[3], p, t)
            g.show("Object moved, select known object with left click, exit with right click")
            g.update()
         
         
   if moving and event == "":
      UpdateMove(curMove, w, h, found[2], found[3], p, t)
   
   handling = False