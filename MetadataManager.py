import golly as g 

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
	
def NewLogicalPattern(cells, inputs, outputs, period):
	result = LogicPattern()
	result.cells = cells
	result.inputs = inputs
	result.outputs = outputs
	result.period = period 
	
	return result
	
class LogicPattern:
	
	def __init__(self):
		self.cells = []
		self.inputs = []
		self.outputs = []
		self.period = -1 
	
	def GetListByOption(self, op):
		
		if op == "in":
			return self.inputs
		else:
			return self.outputs
			
			
class DocPattern:

	def __init__(self, logicPat, location, inetrnal):
		self.logicPat = logicPat
		self.location = location 
		self.internal = internal 
		
class LogicalDoc:
	def __init__(self):
		self.patterns = []
		
	def Add(self, pat):
		self.patterns.append(pat)
		
	def DrawAll(self):
		for pat in self.patterns:
			x, y = pat.location
			g.putcells(g.evolve(pat.logicPat.cells, pat.internal), x, y)
	
class LogicPatternCollection:
	def __init__(self):
		self.patterns = []
		
		self.transList = []
	
		for i in xrange(-1, 2, 2):
			for j in xrange(-1, 2, 2):
				self.transList.append((i, 0, 0, j))
				self.transList.append((0, i, j, 0))


	def Add(self, logicPat):
		
		for t in self.transList:
			dxx, dxy, dyx, dyy = t 
			
			cells = g.transform(logicPat.cells,0, 0, dxx, dxy, dyx, dyy)
			inT = TrnasformDirectionList(logicPat.inputs, t)
			outT = TrnasformDirectionList(logicPat.outputs, t)
			p = logicPat.period
			pat = NewLogicalPattern(cells, inT, outT, p)
			
			self.patterns.append((pat,t))
	
	def FilterByDirection(dir, option):
		
		result = []
		
		for pat in self.patterns:
			logicPat, t = pat
			
			filterList = logicPat.GetListByOption(option)
			
			for i in xrange(0, len(filterList)):
				if dir == TrnasformDirection(i):
					result.append((pat, i))
		
		return result 
				
	def  GetPatternsBySignalClick(self, sigClick):
		sigXY, option = sigClick
		sigTrans, x, y = sigXY
		cells, i, j, k, idx = cellsTrans
		
		return self.FilterByDirection(TrnasformDirection((1, 1), (i, 0, 0, j)), option)
		
		
			
class SignalManager:
	def __init__(self):
		self.signals = []
		
		self.components =  []
		self.components.append(g.parse("bo&2bo$3o!", -1, -1))
		
		for idx in xrange(0, len(self.components)):
			comp = self.components
			
			for i in xrange(-1, 2, 2):
				for j in xrange(-1, 2, 2):
					for k in xrange(0, 4):
						self.signals.append((g.transform(g.evolve(comp, k), 0, 0, i, 0, 0, j), i, j, k, comp))
						
	
	
	def SignalAt(self, x, y):
		for s in self.signals:
			found = True
			
			for i in xrange(0, len(s), 2):
				xs = s[i][0]
				ys = s[i + 1][0]
				
				if g.getcell(x + xs, y + ys) == 0:
					found = False
					break
			
			
			if found:
				return i
				
		return None
		
	def SignalInArea(self, x, y):
	
		for i in xrange(x - 3, x + 4):
			for j in xrange(y - 3, y + 4):
				sig = self.SignalAt(i, j)
				
				if sig != None:
					return (sig, i, j)
					
		
		return None 
	
	def Remove(self, sig):
		s, x, y = sig 
		
		for i in xrange(0, len(s), 2):
			xs = s[i]
			ys = s[i + 1] 
			g.setcell(x + xs, y + ys, 0)

	
	def GetClickOnSignal(self):
		
		g.show("click left for input, right for output")
		
		while True:

			event = g.getevent()
			
			if "click" in event:
				xs, ys = g.getxy().split()
				x = int(xs)
				y = int(ys)
				
				sig = sigMan.SignalInArea(x, y)
				
				if sig != None:
					
					sigMan.Remove(sig)
					
					if "left" in event:
						return (sig, "in")
					if "right" in event:
						return (sig, "out")
						
					
					
					


rle_htog_1 = "31b2o$31b2obo$35bo8bo$32bo9b3o$33bob2o4bo$35b2o4b2o2$39bo13b2o$38bobo12b2o$39b2o2b2o$43b2o2$24bo$24b3o$27bo$26b2o3$15b2ob2o$15b2obo20b2o$18bo19bobo$18b3o4b2o11bo$16b2o3bo3b2o10b2o$15bo2b4o$15b2obo15b2o$16bo2b3o12bobo$16bo5bo13bo11b3o$17b5o14b2o10b3o$19bo28bo2bo6b2o$49b3o6bo$49b2o8b3o$32bobo26bo$33b2o$33bo4$91bo$92bo$48b2o40b3o$48b2o6$59b2o$38b2o19bo$39bo17bobo$39bobo15b2o$40b2o4bo6b2o$45bobo4bo2bo$45bobo5b2o$46bo10b2o$9bo47bobo$9b3o47bo$12bo46b2o5b2o$11b2o31b2o20bo$45bo22bo$42b3o3b2o14b5o$2ob2o37bo6bo13bo$2obo45bobo12b3o$3bo12bo33b2o15bo$3b3o4b2o2b2o48b4o$b2o3bo3b2o3b2o42b2o3bo3b2o$o2b4o52b2o4b3o2bo$2obo15b2o46bob2o$bo2b3o12bobo45bo$bo5bo13bo44b2o$2b5o14b2o$4bo$58b2o$58bo$45b2o12b3o$46b2o13bo$45bo2$34bo$32b3o$31bo$31b2o7$21b2o$20bobo5b2o$20bo7b2o$19b2o2$33bo$29b2obobo$28bobobobo$25bo2bobobob2o$25b4ob2o2bo$29bo4bo$25b2o2bob3o$25b2o3b2o!"
rle_fx119 = "29$59b2o$60bo$60bobo$61b2o4$94bo$92b2o$60b2o$60b2o4b2o$66b2o4$65b2o$61b2o2b2o$60bobo16b3o$60bo12b2o4b3o$59b2o11bobo4bo2bo$72bo7b3o$71b2o7b2o7$122bo$123bo$121b3o6$81b2o$81b2o2$88bob2o$88b2obo3$70b2o$71bo$71bobo$72b2o2$38b2o5b2o$39bo5b2o39b2o$39bobo44bobo$40b2o46bo$44b2o42b2o$45bo4bo$43b2o3bobo$40bo8b2o$39b3o$38bob3o$37bo3bo$36bo3bo42b2o$35b3obo43bo$36b3o45b3o$37bo48bo8$73b2o$73b2o5$74bo$73b3o8b2o$63b2o7b2ob2o7bo$64bo6b2o2bo6bobo$64bobo4b2ob2o6b2o$65b2o5bo5bo$51bo23b2obo$50bo24b2o$50b3o22b2o5b2o$34bo47bobo$34b3o47bo$37bo46b2o$36b2o31b2o22b2o$70bo20bo2bo$67b3o3b2o14b5o$28b2o37bo6bo13bo$28bo45bobo12b3o$25b2obo46b2o15bo$25bo2b3o4b2o52b4o$26b2o3bo3b2o47b2o3bo3b2o$28b4o52b2o4b3o2bo$28bo15b2o46bob2o$29b3o12bobo45bo$32bo13bo44b2o$27b5o14b2o$26bo2bo$26b2o55b2o$83bo$84b3o$86bo3$59bo$57b3o$56bo$56b2o4$59b3o$61bo$60bo$46b2o$45bobo5b2o$45bo8bo$44b2o2$58bo$54b2obobo$53bobobobo$50bo2bo3bob2o$50b4ob2o2bo$54bo4bobo$52bobo5b2o$52b2o!"

sigMan = SignalManager()
recognizables = LogicPatternCollection()
doc = LogicalDoc()

recognizables.Add(NewLogicalPatternRLE(rle_htog_1, (-91, -38), [], [(1, 1)], 160))
recognizables.Add(NewLogicalPatternRLE(rle_fx119, (-97, -29), [], [(1, 1)], 160))


sig = sigMan.GetClickOnSignal()
pats = recognizables.GetPatternsBySignalClick(sig)

doc.Add(DocPattern(pats[0], (sig[0][1], sig[0][2]), 0))
doc.DrawAll()
