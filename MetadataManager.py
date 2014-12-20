import golly as g 
import copy
import json 
import os 

def CellKeyFromXY(x, y):
	return str(x) + ":" + str(y)

def XYIterator():
	
	yield (0, 0)
	
	for i in xrange(-1, 2):
		for j in xrange(-1, 2):
			if i != 0 and j != 0:
				yield (i, j)
	
	for i in xrange(-2, 3):
		for j in xrange(-2, 3):
			if abs(i) == 2 or abs(j) == 2:
				yield (i, j)

	for i in xrange(-3, 4):
		for j in xrange(-3, 4):
			if abs(i) == 3 or abs(j) == 3:
				yield (i, j)
	
def GetDirection(t):
	dxx, dxy, dyx, dyy = t
	
	if dxy == 0:
		return dxx * dyy
	else:
		return dxy * dyx

def GetPositive(t):
	dxx, dxy, dyx, dyy = t
	
	return -(dxx + dxy)
	
def TrnasformDirection(direction, trans):

	dxx, dxy, dyx, dyy = trans 
	x, y = direction	
	
	return (dxx * x + dxy * y, dyx * x + dyy * y)
		
def TrnasformDirectionList(list, trans):
	return [TrnasformDirection(x, trans) for x in list]
	
def NewLogicalPatternRLE(rle, diff, inputs, outputs, period):
	result = LogicPattern()
	x, y = diff
	result.cells = g.parse(rle, x, y)
	result.inputs = inputs
	result.outputs = outputs
	result.period = period 
	
	return result
	
def NewLogicalPattern(cells, inputs, outputs, period, t):
	result = LogicPattern()
	result.cells = cells
	result.inputs = inputs
	result.outputs = outputs
	result.period = period 
	result.t = t 
	
	return result
	
class LogicPattern:
	
	def __init__(self):
		self.cells = []
		self.inputs = []
		self.outputs = []
		self.period = -1 
		self.t = ()

	def ToDict(self):
		return self.__dict__
		
	def FromDict(self, dict):
		for key in dict:
			self.__setattr__(key, dict[key])
		
		
	def GetListByOption(self, op):
		
		if op == "in":
			return self.inputs
		else:
			return self.outputs
	
	def Evolve(self, numIters):
		self.cells = g.evolve(self.cells, numIters)
			
class MovementData:
	def __init__(self, initX, initY, initPat):
		self.under = []
		self.curPat = []
		self.dx = -1
		self.dy = -1
		self.initX = initX 
		self.initY = initY
		self.initPat = initPat
		self.delta = 0 
		
	def RevertState(self):
		for i in xrange(0, len(self.curPat), 2):
			g.setcell(self.curPat[i] + self.dx, self.curPat[i + 1] + self.dy, 0)
		
		g.putcells(self.under)
		
	def UpdateState(self, newPat, dx, dy):
		self.under = []
		self.curPat = newPat
		self.dx = dx
		self.dy = dy
		
		for i in xrange(0, len(self.curPat), 2):
		
			if g.getcell(self.curPat[i] + self.dx, self.curPat[i + 1] + self.dy) == 1:
				self.under.append(self.curPat[i] + self.dx)
				self.under.append(self.curPat[i + 1] + self.dy)
				
			g.setcell(self.curPat[i] + self.dx, self.curPat[i + 1] + self.dy, 1)
		
		g.update()
	
	def UpdateCellDictionary(self, curdict, obejctIdx):
	
		for i in xrange(0, len(self.curPat), 2):
			x = self.curPat[i]
			y = self.curPat[i + 1]
			
			curdict[CellKeyFromXY(x + self.dx, y + self.dy)]  = obejctIdx

	def ClearCellDictionary(self, curdict, obejctIdx):
	
		before = len(curdict)
		removeList = [key for key in curdict if curdict[key] == obejctIdx]
		
		for key in removeList:
			x, y = key.split(":")
			g.setcell(int(x), int(y), 0)
			del curdict[key]
		
		after = len(curdict)
		g.show("size change: " + str(before)  + "," + str(after) + "," + str(obejctIdx))
		
class PlacementSnippet:
	id = 0 
	
	def __init__(self, attachedPatList, idx, moveData):
		self.moveData = moveData
		self.idx = idx 
		self.attachedPatList = attachedPatList
		self.id = PlacementSnippet.id 
		PlacementSnippet.id += 1
	
	def Update(self, attachedPatList, idx, moveData):
		self.moveData = moveData
		self.idx = idx 
		self.attachedPatList = attachedPatList

class LogicalDoc:
	def __init__(self, sigMan, recognizables):
		self.patterns = []
		self.snippets = [] 
		self.smarCells = {}
		self.sigMan = sigMan
		self.recognizables = recognizables

	def ToDict(self):
		dict = self.__dict__
		dict["sigMan"] = self.sigMan.ToDict()
		dict["recognizables"] = self.recognizables.ToDict()
		
		return str(dict)
	
	def FromDict(self):
		
		for key in dict:
			self.__setattr__(key, dict[key])
		
		self.sigMan = SignalManager()
		self.recognizables = LogicPatternCollection()
		
		self.sigMan.FromDict(dict["sigMan"])
		self.recognizables.FromDict(dict["recognizables"])
		
		return str(dict)
	
	def Save(self, file):

		with open(file, 'wb') as fp:
			json.dump(self.ToDict(), fp)
	
	
	def Load(self, file):

		with open(file, 'rb') as fp:
			data = json.load(fp)

		self.FromDict(data)
			
	def Main(self):
		
		g.show("left click on a pattern to change, 'h' for help")
		gollyMode = False
		
		while True:
		
			event = g.getevent()
			
			if ("key" in event and "return" in event) or (gollyMode and " a " in event):
				gollyMode = not gollyMode
				
				if gollyMode:
					g.show("In golly mode")
					g.update()

				else: 
					g.show("left click on a pattern, right click to finish")
					g.setrule("B3/S23")
					g.setalgo("HashLife")
					g.reset()
				
					g.update()
				
				continue 
				
			if gollyMode:
				
				if " delete " in event: 
					g.clear(0)
					
				if "click" in event and "ctrl" in event and g.getxy() != "":
					
					x, y = g.getxy().split()
					
					cell = g.getcell(int(x), int(y))
					
					if cell >= 0 and cell <= 1:
						g.setcell(int(x), int(y), 1 - cell)
					
					g.update()
				
				if " c " in event and "ctrl" in event and g.getselrect() != []:	
					g.copy()
				
				if " v " in event and "ctrl" in event and g.getxy() != "":
				
					x, y = g.getxy().split()
					
					g.paste(int(x), int(y), "or")
				
				if " space " in event:	
					if "ctrl" in event:
						g.run(10)
					else:
						g.run(1)
						
				g.doevent(event)
				continue 
				
			
			if "click" in event:
				
				if "left" in event:
					
					if self.ExistinCircuitHandler() == None:
						if self.SignalClickHandler(event) == None:
							g.show("left click on a pattern, h for help")
		
		
			elif "key" in event:
				if " space " in event:
					for i in xrange(0, 30):
						g.run(60)
						g.update()
						
					g.reset()
					g.update()		
					
				if " a " in event:
					
					if g.getrule() == "Perrier":
						g.setrule("B3/S23")
						g.setalgo("HashLife")
						g.update()
						
						
					else:
						g.setrule("Perrier")
						
						for key in self.smarCells:
							x, y = key.split(":")
							g.setcell(int(x), int(y),  self.smarCells[key] + 2)
						
						gollyMode = True
						g.show("In golly mode")
						g.update()
				
				if " s " in event:
					fname = os.path.join(g.getdir("data"), "MetadataManager.json")
					#self.Save(fname)
				
				if " h " in event:
					noteMessage = "Viewing and Selecting\n\n"
					noteMessage += "'left click' to chose gun or glider\n"
					noteMessage += "'a' to see in colors, a to go back \n"
					noteMessage += "'space' see ahead 1800 generations \n"
					noteMessage += "'enter' gollyMode, stays in the script \n"
					
					noteMessage += "\n Editing Gun \n\n"
					noteMessage += "'left click' to place\n"
					noteMessage += "'right click' to switch gun/orientation \n"
					noteMessage += "'delete' to delete the gun \n"
					noteMessage += "'left-right arrow' - one step adjustment\n"
					
					noteMessage += "\n In Golly Mode \n\n"
					noteMessage += "'delete' to clear selection\n"
					noteMessage += "'ctrl' + 'click' to draw \n"
					noteMessage += "'ctrl' + 'c' to copy selection \n"
					noteMessage += "'ctrl' + 'v' to paste in mouse location \n"
					noteMessage += "'space' + to run 1 generation \n"
					noteMessage += "'ctrl' +'space' to run 10 generations \n"
				
					g.note(noteMessage)
					
	def ExistinCircuitHandler(self):
		snip = self.ExitingSnippet()
		
		if snip == None:
			return None
		
		snip.moveData.ClearCellDictionary(self.smarCells, snip.id)
		self.ManageSnippet(snip)
		
	def ExitingSnippet(self):
	
		if g.getxy() == "":
			return None
			
		xs, ys = g.getxy().split()
		x = int(xs)
		y = int(ys)
					
		
		for i, j in XYIterator():
			key = CellKeyFromXY(x + i, y + j)
			if key in self.smarCells:
				return self.snippets[self.smarCells[key]]
	
		return None
		
	def SignalClickHandler(self, event):
		sigIn = sigMan.GetClickOnSignal(event)
		
		if sigIn != None:
			sig, op = sigIn
			pats = recognizables.GetPatternsBySignalClick((sig, op), sigMan)
			self.ManagePlacement(pats)
	
	def GetMovementData(self, attachedPatList, idx):
		
		return MovementData(attachedPatList[idx].x, attachedPatList[idx].y,	attachedPatList[idx].logicPat.cells)
			
	def ManagePlacement(self, attachedPatList):
		idx = 0
		movementData = self.GetMovementData(attachedPatList, idx)
		self.Placement(movementData, idx, attachedPatList, None)
		
	def ManageSnippet(self, snippet):

		self.Placement(snippet.moveData, snippet.idx, snippet.attachedPatList, snippet)
		
		
	def Placement(self, movementData, idx, attachedPatList, snip):
		
		while True:
		
			event = g.getevent()
			
			if event == "":
				self.ManageMove(attachedPatList[idx], movementData)
				
			elif "click" in event:
				
				if "right" in event: 
			
					movementData.RevertState()
					idx = (idx + 1) % len(attachedPatList)
					
					movementData = self.GetMovementData(attachedPatList, idx)
					self.ManageMove(attachedPatList[idx], movementData)
					
				elif "left" in event: 
					
					if snip == None:
						snip = PlacementSnippet(attachedPatList, idx, movementData)
						self.snippets.append(snip)
					else:
						snip.Update(attachedPatList, idx, movementData)
						
					movementData.UpdateCellDictionary(self.smarCells, snip.id)
					
					return 
				
			elif "key" in event:
				if "space" in event:
					for i in xrange(0, 30):
						g.run(60)
						g.update()
						
					g.reset()
					g.update()
				
				elif "right" in event:
					movementData.delta += 1
					
				elif "left" in event:
					movementData.delta -= 1
				
				elif "delete" in event: 
				
					movementData.RevertState()
					g.update()
					return 
			
				
	def ManageMove(self, attachedPat, movementData):
		
		val = g.getxy()
		
		if val == "":
			return 
		
		x1 = int(val.split()[0]) + movementData.delta
		self.MoveToX(attachedPat, x1, movementData)
		
		
	def MoveDelta(self, attachedPat, movementData, delta):
		movementData.RevertState()
		movementData.dx += delta * GetPositive(attachedPat.logicPat.t)
		self.MoveToX(attachedPat, movementData.dx, movementData)
		
	def MoveToX(self, attachedPat, x1, movementData):
		
		if  (x1 - movementData.initX) * GetPositive(attachedPat.logicPat.t)  < 0:
			x1 = movementData.initX
		
		y1 = movementData.initY + GetDirection(attachedPat.logicPat.t) * (x1 - movementData.initX)
		
		movementData.RevertState()
		movementData.UpdateState(g.evolve(movementData.initPat, 4 *  (x1 - movementData.initX) * GetPositive(attachedPat.logicPat.t)), x1, y1)
		
		
	def DrawAll(self):
		for pat in self.patterns:
			x, y = pat.location
			g.putcells(g.evolve(pat.attachedPat.logicPat.cells, pat.internal), x, y)

class AttachedLogicPat:
	def __init__(self, pat, i, option, x, y):
		self.logicPat = pat
		self.option = option 
		self.index = i
		self.x = x
		self.y = y 
	
	def ToDict(self):	
		dict = self.__dict__

		dict["logicPat"] = self.logicPat.ToDict()
		
	def FromDict(self, dict):	

		for key in dict:
			self.__setattr__(key, dict[key])
		
		self.logicPat = LogicPat()
		self.logicPat.FromDict(dict["logicPat"])
		 
	def Evolve(self, numIter):
		self.logicPat.Evolve(numIter)
		
	
class LogicPatternCollection:
	def __init__(self):
		self.patterns = []
		self.transList = []

		for i in xrange(-1, 2, 2):
			for j in xrange(-1, 2, 2):
				self.transList.append((i, 0, 0, j))
				self.transList.append((0, i, j, 0))

	
	def ToDict(self):
		dict = self.__dict__
		dict["patterns"] = [x.ToDict() for x in self.patterns]
		
		return dict 
		
	def FromDict(self, dict):
		for key in dict:
			self.__setattr__(key, dict[key])
		
		for i in xrange(0, len(self.patterns)):
			dict = self.patterns[i]
			self.patterns[i] = LogicPattern()
			self.patterns[i].FromDict(dict)
			
	def Add(self, logicPat):
		
		for t in self.transList:
			dxx, dxy, dyx, dyy = t 
			
			cells = g.transform(logicPat.cells,0, 0, dxx, dxy, dyx, dyy)
			
			if dxx == 0:
				cells = g.transform(g.evolve(cells, 2), -dxy, 0)
				
			inT = TrnasformDirectionList(logicPat.inputs, t)
			outT = TrnasformDirectionList(logicPat.outputs, t)
			p = logicPat.period
			pat = NewLogicalPattern(cells, inT, outT, p, t)
			
			self.patterns.append(pat)
	
	def FilterByDirection(self, dir, option):
		
		result = []
		
		for pat in self.patterns:

			filterList = pat.GetListByOption(option)
			
			for i in xrange(0, len(filterList)):
				if dir == filterList[i]:
					result.append(AttachedLogicPat(pat, i, option, 0, 0))
		
		return result 
				
	def  GetPatternsBySignalClick(self, sigClick, sigMan):
		physSig, option = sigClick
		cells, i, j, k, idx = sigMan.GetSignalFullData(physSig.signal)
		
		#bug fix not to evolve the setup data
		result = copy.deepcopy(self.FilterByDirection(TrnasformDirection((1, 1), (i, 0, 0, j)), option))

		for r in result:
			r.Evolve(k)
			r.x = physSig.x
			r.y = physSig.y
			
		return result
		
		
class PhysicalSignal:
	def __init__(self, sig, x, y):
		self.signal = sig
		self.x = x 
		self.y = y
		
	def Location(self):
		return (self.x, self.y)
		
class SignalManager:
	def __init__(self):
		self.signalsFullData = []
		self.signals = []
		
		self.components =  [g.parse("bo$2bo$3o!", -1, -1)]

		for idx in xrange(0, len(self.components)):
			comp = self.components[idx]
			
			for i in xrange(-1, 2, 2):
				for j in xrange(-1, 2, 2):
					for k in xrange(0, 4):
						self.signalsFullData.append((g.transform(g.evolve(comp, k), 0, 0, i, 0, 0, j), i, j, k, idx))
						self.signals.append(g.transform(g.evolve(comp, k), 0, 0, i, 0, 0, j))

						
	def ToDict(self):
		return self.__dict__
	
	def FromDict(self, dict):
		for key in dict:
			self.__setattr__(key, dict[key])
			
		
	def GetSignalFullData(self, sig):
		
		for i in xrange(0, len(self.signals)):
				if sig == self.signals[i]:
					return self.signalsFullData[i]
		
		return None
		
	def SignalAt(self, x, y):
		
		for s in self.signals:
			found = True
			
			for i in xrange(0, len(s), 2):
				xs = s[i]
				ys = s[i + 1]
				
				if g.getcell(x + xs, y + ys) == 0:
					found = False
					break
			
			
			if found:
				return s
				
		return None
		
	def SignalInArea(self, x, y):
	
		for i in xrange(x - 1, x + 2):
			for j in xrange(y - 1, y + 2):
				sig = self.SignalAt(i, j)
				
				if sig != None:
					return PhysicalSignal(sig, i, j)
					
		
		return None 
	
	def Remove(self, phisSig):
		
		for i in xrange(0, len(phisSig.signal), 2):
			xs = phisSig.signal[i]
			ys = phisSig.signal[i + 1] 
			
			g.setcell(phisSig.x + xs, phisSig.y + ys, 0)

	
	def GetClickOnSignal(self, event):
		
		xs, ys = g.getxy().split()
		x = int(xs)
		y = int(ys)
		
		sig = sigMan.SignalInArea(x, y)
		
		if sig != None:
			
			#sigMan.Remove(sig)
			
			if "left" in event:
				return (sig, "out")
			if "right" in event:
				return (sig, "out")

sigMan = SignalManager()
recognizables = LogicPatternCollection()

#rle_htog_1 = "31b2o$31b2obo$35bo8bo$32bo9b3o$33bob2o4bo$35b2o4b2o2$39bo13b2o$38bobo12b2o$39b2o2b2o$43b2o2$24bo$24b3o$27bo$26b2o3$15b2ob2o$15b2obo20b2o$18bo19bobo$18b3o4b2o11bo$16b2o3bo3b2o10b2o$15bo2b4o$15b2obo15b2o$16bo2b3o12bobo$16bo5bo13bo11b3o$17b5o14b2o10b3o$19bo28bo2bo6b2o$49b3o6bo$49b2o8b3o$32bobo26bo$33b2o$33bo4$91bo$92bo$48b2o40b3o$48b2o6$59b2o$38b2o19bo$39bo17bobo$39bobo15b2o$40b2o4bo6b2o$45bobo4bo2bo$45bobo5b2o$46bo10b2o$9bo47bobo$9b3o47bo$12bo46b2o5b2o$11b2o31b2o20bo$45bo22bo$42b3o3b2o14b5o$2ob2o37bo6bo13bo$2obo45bobo12b3o$3bo12bo33b2o15bo$3b3o4b2o2b2o48b4o$b2o3bo3b2o3b2o42b2o3bo3b2o$o2b4o52b2o4b3o2bo$2obo15b2o46bob2o$bo2b3o12bobo45bo$bo5bo13bo44b2o$2b5o14b2o$4bo$58b2o$58bo$45b2o12b3o$46b2o13bo$45bo2$34bo$32b3o$31bo$31b2o7$21b2o$20bobo5b2o$20bo7b2o$19b2o2$33bo$29b2obobo$28bobobobo$25bo2bobobob2o$25b4ob2o2bo$29bo4bo$25b2o2bob3o$25b2o3b2o!"
#rle_fx119 = "29$59b2o$60bo$60bobo$61b2o4$94bo$92b2o$60b2o$60b2o4b2o$66b2o4$65b2o$61b2o2b2o$60bobo16b3o$60bo12b2o4b3o$59b2o11bobo4bo2bo$72bo7b3o$71b2o7b2o7$122bo$123bo$121b3o6$81b2o$81b2o2$88bob2o$88b2obo3$70b2o$71bo$71bobo$72b2o2$38b2o5b2o$39bo5b2o39b2o$39bobo44bobo$40b2o46bo$44b2o42b2o$45bo4bo$43b2o3bobo$40bo8b2o$39b3o$38bob3o$37bo3bo$36bo3bo42b2o$35b3obo43bo$36b3o45b3o$37bo48bo8$73b2o$73b2o5$74bo$73b3o8b2o$63b2o7b2ob2o7bo$64bo6b2o2bo6bobo$64bobo4b2ob2o6b2o$65b2o5bo5bo$51bo23b2obo$50bo24b2o$50b3o22b2o5b2o$34bo47bobo$34b3o47bo$37bo46b2o$36b2o31b2o22b2o$70bo20bo2bo$67b3o3b2o14b5o$28b2o37bo6bo13bo$28bo45bobo12b3o$25b2obo46b2o15bo$25bo2b3o4b2o52b4o$26b2o3bo3b2o47b2o3bo3b2o$28b4o52b2o4b3o2bo$28bo15b2o46bob2o$29b3o12bobo45bo$32bo13bo44b2o$27b5o14b2o$26bo2bo$26b2o55b2o$83bo$84b3o$86bo3$59bo$57b3o$56bo$56b2o4$59b3o$61bo$60bo$46b2o$45bobo5b2o$45bo8bo$44b2o2$58bo$54b2obobo$53bobobobo$50bo2bo3bob2o$50b4ob2o2bo$54bo4bobo$52bobo5b2o$52b2o!"
#recognizables.Add(NewLogicalPatternRLE(rle_htog_1, (-91, -38), [], [(1, 1)], 160))
#recognizables.Add(NewLogicalPatternRLE(rle_fx119, (-122, -58), [], [(1, 1)], 160))

rle_htog_1 = "31b2o$31b2obo$35bo8bo$32bo9b3o$33bob2o4bo$35b2o4b2o2$39bo13b2o$38bobo12b2o$39b2o2b2o$43b2o$54b2o$24bo15b2o11bo4bo$24b3o13bobo9bo5bo4b2o$27bo12bo11b2ob2obo3bo2bo$26b2o33b2obo4bo$55bo6bobo5bo$55bo7b3o2b3o$15b2ob2o34bo10bo$15b2obo20b2o11b2o$18bo19bobo13bo$18b3o4b2o11bo13b2o$16b2o3bo3b2o10b2o$15bo2b4o$15b2obo15b2o$16bo2b3o12bobo$16bo5bo13bo$17b5o14b2o$19bo38b2o$58bo$59b3o$61bo8$48b2o$38bo9b2o$36b2o$37b2o4$59b2o$38b2o19bo$39bo17bobo$39bobo15b2o$40b2o4bo$45bobo$45bobo$46bo10b2o$9bo47bobo$9b3o47bo$12bo41b2o3b2o5b2o$11b2o31b2o7b2o11bo$45bo9bo12bo$42b3o3b2o14b5o$2ob2o37bo6bo13bo$2obo45bobo12b3o$3bo46b2o15bo$3b3o4b2o52b4o$b2o3bo3b2o47b2o3bo3b2o$o2b4o52b2o4b3o2bo$2obo15b2o46bob2o$bo2b3o12bobo45bo$bo5bo13bo44b2o$2b5o14b2o$4bo$58b2o$58bo$59b3o$61bo3$34bo$32b3o$24bo6bo$25b2o4b2o$24b2o6$21b2o$20bobo5b2o$20bo7b2o$19b2o2$33bo$29b2obobo$28bobobobo$25bo2bobobob2o$25b4ob2o2bo$29bo4bo$25b2o2bob3o$25b2o3b2o!"
rle_fx119 = "34b2o$35bo$35bobo22b2o$36b2o21bo4bo$58bo5bo4b2o$58b2ob2obo3bo2bo$48b4o15b2obo4bo$47b3ob2o8bo6bobo5bo$45bo3bo2b2o7bo7b3o2b3o$35b2o8bo2bo3bo7bo10bo$35b2o8bobo3bo6b2o$60bo$58b2o3$40b2o$36b2o2b2o$35bobo24b2o$35bo12b2o12b2o$34b2o11bobo$47bo$46b2o10$44bo$42b2o$43b2o3$56b2o$56b2o2$63bob2o$63b2obo3$45b2o$46bo$46bobo$47b2o2$13b2o5b2o31bo$14bo5b2o30b3o6b2o$14bobo34bo2bo6bobo$15b2o33b3o2b2o6bo$19b2o30bo2b3o6b2o$18bobo31b2o2b2o$19bo35b3o$15bo36b4obo$14b3o35b2o2b2o$13bob3o37b2o$12bo3bo$11bo3bo42b2o$10b3obo33bo9bo$11b3o33bo11b3o$12bo34b3o11bo8$48b2o$43bo4b2o$41bobo$42b2o4$59b2o$38b2o19bo$39bo17bobo$39bobo15b2o$40b2o4bo6b2o$45bobo4bo2bo$45bobo5b2o$46bo10b2o$9bo47bobo$9b3o47bo$12bo46b2o$11b2o31b2o22b2o$45bo20bo2bo$42b3o3b2o14b5o$3b2o37bo6bo13bo$3bo45bobo12b3o$2obo5b2o39b2o15bo$o2b2o6bo52b4o$b2o2bo2bob2o47b2o3bo3b2o$3bob2o52b2o4b3o2bo$3bobo13b2o31b3o12bob2o$4b3o12bobo32bo12bo$7bo6bo6bo31bo12b2o$2b5o8bo5b2o$bo2bo8b3o$b2o55b2o$58bo$59b3o$61bo3$34bo$32b3o$31bo$31b2o7$21b2o$20bobo5b2o$20bo7b2o$19b2o2$33bo$29b2obobo$28bobobobo$25bo2bobobob2o$25b4ob2o2bo$29bo4bobo$27bobo5b2o$27b2o!"
recognizables.Add(NewLogicalPatternRLE(rle_htog_1, (-69, -16), [], [(1, 1)], 160))
recognizables.Add(NewLogicalPatternRLE(rle_fx119, (-75, -7), [], [(1, 1)], 160))

doc = LogicalDoc(sigMan, recognizables)
#fname = os.path.join(g.getdir("data"), "MetadataManager.json")

#if os.path.exists(fname):
#	doc.Load(fname)

#doc.Save(fname)

doc.Main()

