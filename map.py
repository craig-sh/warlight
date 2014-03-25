from __future__ import print_function
import sys
from region import SuperRegion,Region
from collections import deque
class Map(object):
    def __init__(self):
        self.regions = {}
        self.super_regions = {}
        self.clean_up_queue = deque()
        self.visible_regions = []
    def add_super_region(self,super_region_id,bonus):
        self.super_regions[super_region_id] = (SuperRegion(super_region_id,bonus))
    def add_region(self,region_id,super_region_id):
        self.regions[region_id] = (Region(region_id,self.super_regions[super_region_id]))
        self.super_regions[super_region_id].add_child(self.regions[region_id])
    def add_neighbors(self,region_id,neighbors):
        if not type(region_id) is str:
            print("ERROR: region id ",str(region_id), " must be int",file=sys.stderr)
        for neighbor in neighbors:
            #Add a bi-directional refrence between neighbors
            self.regions[region_id].add_neighbor(self.regions[neighbor])
            self.regions[neighbor].add_neighbor(self.regions[region_id])

    def shortest_path(self,region_from, region_to):
        #FIXME
        print ("TODO")

    def fill_queue(self):
        for region in self.regions:
            self.queue.append(region)

#    def get_path(self,soruce,dest,path):
#        #This will return list of id's for the regions
#        #on the shortest path
#        if source == dest:
#            return
#        elif dest.pi == None:
#            print ("ERROR: No path exists",file=sys.stderr)
#            return None
#        else :
#            path.append(dest.id)
#            return get_path(self,source,dest.pi,path)

#    def BFS(self,source):
#        source.color = 'GRAY'
#        source.dis = 0
#        source.pi = None
#        queue = deque([self.regions[source]])
#        while len(queue) != 0:
#            u = queue.pop()
#            self.clean_up_queue.append(u)
#            for v in u.neighbors:
#                if v.color == 'WHITE':
#                    v.color = 'GRAY'
#                    v.dis = u.dis + 1
#                    v.pi = u
#                    queue.appendLeft(v)
#            #not really needed
#            u.color = 'BLACK'
#
#
#    def clean_up(self):
#        for region in self.clean_up_queue:
#            region.color = 'WHITE'
#            region.dis = float('inf')
#            region.pi = None
#        self.clean_up_queue.clear()

    def update_region(self,region_id, occupant, armies):
        self.regions[region_id].occupant = occupant
        self.regions[region_id].armies = int(armies)






