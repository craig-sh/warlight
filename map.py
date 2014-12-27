from __future__ import print_function
import sys
from region import SuperRegion, Region
from collections import deque


class Map(object):

    def __init__(self):
        self.regions = {}
        self.super_regions = {}
        self.clean_up_queue = deque()
        self.visible_regions = []

    def add_super_region(self, super_region_id, bonus):
        self.super_regions[super_region_id] = (
            SuperRegion(super_region_id, bonus))

    def add_region(self, region_id, super_region_id):
        self.regions[region_id] = (
            Region(region_id, self.super_regions[super_region_id]))
        self.super_regions[super_region_id].add_child(self.regions[region_id])

    def add_neighbors(self, region_id, neighbor_ids):
        if not type(region_id) is str:
            print("ERROR: region id ", str(region_id),
                  " must be int", file=sys.stderr)
        for neighbor in neighbor_ids:
            # Add a bi-directional refrence between neighbors
            self.regions[region_id].add_neighbor(self.regions[neighbor])
            self.regions[neighbor].add_neighbor(self.regions[region_id])

    def weight_super_regions(self):
        for sid, super_region in self.super_regions.items():
            weight = len(super_region.children)
            super_region.weighted_bonus = super_region.bonus / weight

    def shortest_path(self, region_from, region_to):
        # FIXME
        print("TODO")

    def fill_queue(self):
        for region in self.regions:
            self.queue.append(region)

    """
    Returns the optimal path from source to dest
    in the path variable in reverse order
    Doesn't care about who owns things on the path
    #FIXE - make path a queue not a list
    """

    def get_path(self, source, dest, path):
        # This will return list of id's for the regions
        # on the shortest path

        if dest is None or dest.pi is None:
            #print ("ERROR: No path exists",file=sys.stderr)
            return None
        if source == dest:
            path.append(source.id)
            return
        else:
            path.append(dest.id)
            return self.get_path(source, dest.pi, path)

    """
    Returns the closest node that
    matches the terminate condition
    """

    def BFS(self, source, terminate_case=None):
        source.color = 'GRAY'
        source.dis = 0
        source.pi = None
        queue = deque()
        queue.append(source)
        while len(queue) != 0:
            u = queue.pop()
            self.clean_up_queue.append(u)
            for v in u.neighbors:
                if v.color == 'WHITE':
                    v.color = 'GRAY'
                    v.dis = u.dis + 1
                    v.pi = u
                    queue.appendleft(v)
                    self.clean_up_queue.append(v)
                # if we found what we are looking for just exit
                if terminate_case(v):
                    return v
            # not really needed
            u.color = 'BLACK'

    def safe_BFS(self, source, terminate_case):
        source.color = 'GRAY'
        source.dis = 0
        source.pi = None
        queue = deque()
        queue.append(source)
        while len(queue) != 0:
            u = queue.pop()
            self.clean_up_queue.append(u)
            for v in u.neighbors:
                if v.color == 'WHITE' and v.occupant != 'neutral':
                    v.color = 'GRAY'
                    v.dis = u.dis + 1
                    v.pi = u
                    queue.appendleft(v)
                    self.clean_up_queue.append(v)
                # if we found what we are looking for just exit
                if terminate_case(v):
                    return v
            # not really needed
            u.color = 'BLACK'

    def clean_up(self):
        for region in self.clean_up_queue:
            region.color = 'WHITE'
            region.dis = float('inf')
            region.pi = None
        self.clean_up_queue.clear()

    def update_region(self, region_id, occupant, armies):
        self.regions[region_id].occupant = occupant
        self.regions[region_id].armies = int(armies)

    def closest_unowned_region(self, region):
        path = []
        dest = self.BFS(region, lambda x: x.occupant != region.occupant)
        self.get_path(region, dest, path)
        #print ("Path:",path,file=sys.stderr)
        self.clean_up()
        return path

    def closest_enemy(self, region):
        path = []
        dest = self.BFS(
            region, lambda x: x.occupant != region.occupant and x.occupant != 'neutral')
        self.get_path(region, dest, path)
        self.clean_up()
        return path

    def safest_path_to_enemy(self, region):
        path = []
        dest = self.safe_BFS(
            region, lambda x: x.occupant != region.occupant and x.occupant != 'neutral')
        self.get_path(region, dest, path)
        self.clean_up()
        return path

    def get_importance(self, region):
        """ Returns a score based on the stategic imporance of a region
        """
        score = 0
        if region.super_region.remaining_regions > 0:
            score += float(1)/region.super_region.remaining_regions

        return score + 1.0

    def get_placement_score(self, region, name, opponent_name,
                            placements, last_move=0):
        SURVIVAL = 0.4
        score = 0
        #A region is a scout if it no adjacent region belongs to the enemy
        ####
        #psuedocode
        #for each neighbor
        # if we can defend w/o reinforcements + 0 points
        # if we have an oppenent neighbor in the same super region that
        # we cantake over w/ reinforcements + x points(scale this inversly with # of regions till we own it)
        #
        #
        #
        ####

        score = 0
        for neighbor in region.neighbors:
            new_units = region.armies + placements
            #current_ratio = float(enemy_units) / float(units)
            #new_ratio = float(enemy_units) / (float(new_units))
            #diff = abs(new_ratio - current_ratio)
            if region.can_defend(neighbor) is True and region.can_attack(neighbor) is False:
                if region.can_attack(neighbor, new_units):
                    score += 1.0 * self.get_placement_score(neighbor)
            elif region.can_defend(neighbor, new_units) is True and region.can_attack(neighbor) is False:
                score += 1.0
            elif region.can_defend(neighbor, new_units) > SURVIVAL:
                score += 0.75

        #for neighbor in region.neighbors:
        #    if neighbor.occupant == 'neutral':
        #        if neighbor.super_region == region.super_region and \
        #           region.super_region.remaining_regions <= 2:
        #            if neighbor.strongest(name) == region and \
        #               region.armies < 5:
        #                score += 3.0 + 1.0 * last_move
        #        elif neighbor.super_region == region.super_region:
        #            score += 0.4 + last_move * 0.5
        #        else:
        #            score += 0.2 + last_move * 0.5
        #        if int(neighbor.super_region.id) == 5:
        #            score = score / 5.0
                #print ("LOLs",file=sys.stderr)

        return score

        # Placement scores
        # 1. enemy beside you
        # 2. Don't want to expand out of continent before capturing it
        # 3. Want to weight caputuring a continent before attacking an enemy
    def get_attacks(self, region, name, opponent_name):
        moves = {}
        SAFETY_NET = 1.7
        SCOUT_FORCE = 4
        RISKY_SCOUT = False
        HIGH_NUM = 1000
        armies = region.armies - 1
        safe = True
        for neighbor in region.neighbors:
            if neighbor.occupant == opponent_name:
                safe = False
                if float(armies) / float(neighbor.armies) < SAFETY_NET:
                    if neighbor.total_adversaries(name) > \
                            float(neighbor.armies) * SAFETY_NET:

                        moves[neighbor] = armies + 1 * int(
                            region.same_super(neighbor)) + HIGH_NUM
                else:
                    moves[neighbor] = float(armies) + 1 * int(
                        region.same_super(neighbor)) + HIGH_NUM
        if safe:
            for neighbor in region.neighbors:
                if neighbor.occupant == 'neutral':
                    if armies >= SCOUT_FORCE:
                        moves[neighbor] = SCOUT_FORCE + 1 * int(
                            region.same_super(neighbor))
        return moves
