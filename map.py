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
        self.super_regions[super_region_id] = (SuperRegion(super_region_id, bonus))

    def add_region(self, region_id, super_region_id):
        self.regions[region_id] = (Region(region_id, self.super_regions[super_region_id]))
        self.super_regions[super_region_id].add_child(self.regions[region_id])

    def set_wasteland(self, region_id):
        #FIXME -- Is this 10?
        self.region[region_id].armies = 10

    def add_neighbors(self, region_id, neighbors):
        if not type(region_id) is str:
            print("ERROR: region id ", str(region_id), " must be int", file=sys.stderr)
        for neighbor in neighbors:
            # Add a bi-directional refrence between neighbors
            self.regions[region_id].add_neighbor(self.regions[neighbor])
            self.regions[neighbor].add_neighbor(self.regions[region_id])

    def weight_super_regions(self):
        for super_region in self.super_regions:
            weight = len(super_region.children)
            super_region.weighted_bonus = super_region.bonus / weight

    def shortest_path(self, region_from, region_to):
        # FIXME
        print ("TODO")

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

    def BFS(self, source, terminate_case):
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
        dest = self.BFS(region, lambda x: x.occupant != region.occupant and x.occupant != 'neutral')
        self.get_path(region, dest, path)
        print ("Path:", path, file=sys.stderr)
        self.clean_up()
        return path

    def get_placement_score(self, region, name, opponent_name):
        DEFENSE = 0.9
        ATTACK = 1.5
        SCOUT = 0.2
        FILL_CONTINENTS = 3
        MINIMUM_SCOUT_FORCE = 5
        super_region = region.super_region
        threat = {}
        score = 0
        for neighbor in region.neighbors:
            if neighbor.occupant == opponent_name:
                if neighbor.super_region == region.super_region and \
                   region.super_region.remaining_regions <= 2:
                    if neighbor.strongest(name) == region:
                        score += 2.0
                        #float(neighbor.armies)/float(region.armies) *2* ATTACK
                    # elif float(region.armies)/float(neighbor.armies) < ATTACK:
                    #    pass
                elif float(region.armies) / float(neighbor.armies) \
                        < float(DEFENSE):
                    if(neighbor.strongest(name) == region):
                        score += 1.0
                    # float(neighbor.armies)/float(region.armies)
                    # else:
                    #    pass

                # elif (region.armies - neighbor.armies)/region.armies \
                #   < (ATTACK):
                #    score += 1
                else:
                    score += 0.5
                    #(float(neighbor.armies)/float(region.armies)) / 2.0
            elif neighbor.occupant == 'neutral':
                if neighbor.super_region == region.super_region and \
                   region.super_region.remaining_regions <= 2 and \
                   region.armies < MINIMUM_SCOUT_FORCE:
                    if neighbor.strongest(name) == region:
                        score += 1.5
                        # float(FILL_CONTINENTS) * float(((len(region.super_region.children) \
                        #        - region.super_region.remaining_regions)/ \
                        #        float(len(region.super_region.children))))
                elif region.armies < MINIMUM_SCOUT_FORCE:
                    if neighbor.super_region == region.super_region:
                        if neighbor.strongest(name) == region and neighbor.strongest(name).armies < MINIMUM_SCOUT_FORCE:
                            score += 0.75
                            #score += 2*SCOUT + 0.25*region.armies
                    else:
                        score += 0.25

        return score

        # Placement scores
        # 1. enemy beside you
        # 2. Don't want to expand out of continent before capturing it
        # 3. Want to weight caputuring a continent before attacking an enemy

    def get_attack_score(self, reigon, name, opponent_name):
        pass
