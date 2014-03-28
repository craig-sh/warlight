class SuperRegion(object):
    def __init__(self,i,bonus):
        self.id = i
        self.bonus = int(bonus)
        self.weighted_bonus = 0
        self.children = []
        self.remaining_regions = 1000
    def add_child(self,child):
        #neighnor should be an object this will
        #be similar to an array of pointers?
        self.children.append(child)

    def is_owned(self,name):
        total_regs = 0
        for region in self.children:
            if region.occupant == name:
                total_regs += 1
        if float(total_regs)/float(len(self.children)) > 0.5:
            return True
        else:
            return False


class Region(object):
    def __init__(self,i,super_region):
        self.id = i
        self.super_region = super_region
        self.neighbors = []
        self.occupant = 'neutral'
        self.armies = 0
        self.last_army = 0
        self.color = 'WHITE'
        self.dis = float('inf')
        self.pi = None



    def add_neighbor(self,neighbor):
        #neighnor should be an object this will
        #be similar to an array of pointers?
        self.neighbors.append(neighbor)

    def same_super(self,neighbor):
        return self.super_region == neighbor.super_region

    def strongest(self,name,condition=None):
        highest = None
        for neighbor in self.neighbors:
            if not condition or condition(neighbor):
                if neighbor.occupant == name:
                    if ( highest == None) or (highest.armies < neighbor.armies):
                        highest = neighbor
        return highest

    def total_adversaries(self,name,condition):
        armies = 0
        for neighbor in self.neighbors:
            if neighbor.occupant == name:
                armies += neighbor.armies
        return armies

