class SuperRegion(object):

    def __init__(self, i, bonus):
        self.id = i
        self.bonus = int(bonus)
        self.weighted_bonus = 0
        self.children = []
        self.remaining_regions = 1000

    def add_child(self, child):
        # neighnor should be an object this will
        # be similar to an array of pointers?
        self.children.append(child)


class Region(object):

    def __init__(self, i, super_region):
        self.id = i
        self.super_region = super_region
        self.neighbors = []
        self.occupant = 'neutral'
        self.armies = 0
        self.last_army = 0
        self.color = 'WHITE'
        self.dis = float('inf')
        self.pi = None

    def add_neighbor(self, neighbor):
        # neighnor should be an object this will
        # be similar to an array of pointers?
        self.neighbors.append(neighbor)

    def strongest(self, name):
        highest = None
        for neighbor in self.neighbors:
            if neighbor.occupant == name:
                if (highest is None) or (highest.armies < neighbor.armies):
                    highest = neighbor
        return highest
