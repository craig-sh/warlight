class SuperRegion(object):
	def __init__(self,i,bonus):
		self.id = i
		self.bonus = int(bonus)
		self.children = []
	def add_child(self,child):
		#neighnor should be an object this will
		#be similar to an array of pointers?
		self.children.append(child)

class Region(object):
	def __init__(self,i,super_region):
		self.id = i
		self.super_region = super_region 
		self.neighbors = []
		self.occupant = None
		self.color = 'WHITE'
		self.dis = float('inf')
		self.pi = None



	def add_neighbor(self,neighbor):
		#neighnor should be an object this will
		#be similar to an array of pointers?
		self.neighbors.append(neighbor)

