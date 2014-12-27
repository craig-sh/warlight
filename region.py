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

    def get_num_owned(self, name):
        return sum(1 for reg in self.children if reg.occupant == name)

    def is_owned(self, name):
        total_regs = 0
        for region in self.children:
            if region.occupant == name:
                total_regs += 1
        if float(total_regs) / float(len(self.children)) >= 0.5:
            return True
        else:
            return False


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
        self.placement_score = 0
        self.attack_score = 0

    def add_neighbor(self, neighbor):
        # neighnor should be an object this will
        # be similar to an array of pointers?
        self.neighbors.append(neighbor)

    def same_super(self, neighbor):
        return self.super_region == neighbor.super_region

    def strongest(self, name, condition=None):
        highest = None
        for neighbor in self.neighbors:
            if not condition or condition(neighbor):
                if neighbor.occupant == name:
                    if highest is None or (highest.armies < neighbor.armies):
                        highest = neighbor
        return highest

    def total_adversaries(self, name):
        armies = 0
        for neighbor in self.neighbors:
            if neighbor.occupant == name:
                armies += neighbor.armies - 1
        return armies

    """
    Retrurns a how many armies to attack with specifying if 'neighbor'
    can be safely attacked
    """

    def can_attack(self, neighbor, armies=None):
        if not armies:
            armies = self.armies
        SAFETY_UNITS = 6
        SAFETY_FACTOR = 1.3
        ATTACK_LEAD = 8
        DONT_CARE = 100
        enemy_units = self.total_adversaries(neighbor.occupant) + SAFETY_UNITS
        if enemy_units <= 1:
            return 3
        if armies > float(enemy_units) * SAFETY_FACTOR:
            safe_attack_force = int(float(enemy_units) * SAFETY_FACTOR) + ATTACK_LEAD
            return min(safe_attack_force, armies)
        elif armies >= (enemy_units + ATTACK_LEAD*2) and enemy_units >= DONT_CARE:
            return armies
        else:
            return False

    def can_defend(self, neighbor, armies=None):
        if neighbor.occupant == 'neutral':
            return True

        if not armies:
            armies = self.armies
        SAFETY_UNITS = 2
        DEFENSE_FACTOR = 0.9
        enemy_units = float(
            self.total_adversaries(neighbor.occupant) + SAFETY_UNITS)
        if enemy_units < 1:
            return True
        ratio = float(armies) / enemy_units
        if ratio > DEFENSE_FACTOR:
            return True
        else:
            return ratio
