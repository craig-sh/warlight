from __future__ import print_function
import sys
from sys import stdin, stdout
from map import Map


class Bot(object):

    def __init__(self):
        self.name = ""
        self.map = Map()
        self.start_armies = 0
        self.opponent_name = ""
        self.last_move = 0

    """
    Updates each super region with the number of remaining
    regions in them that are left to capture
    """

    def update_super_regions(self):
        for super_region in self.map.super_regions.values():
            super_region.remaining_regions = 0
            for region in super_region.children:
                if region.occupant != self.name:
                    super_region.remaining_regions += 1

    """
    Tries and group picks into the same super region
    Consider evaluating the distances between all picks as well
    """

    def start_pick(self, regions):
        count = {}
        picks = {}
        picks_left = 6
        # self.map.weight_super_regions()
        for region in regions:
            super_region = self.map.regions[region].super_region
            if not super_region in count:
                count[super_region] = 0
                picks[super_region] = []
            count[super_region] += super_region.bonus
            picks[super_region].append(region)
        outStr = ""
        for w in sorted(count, key=count.get):
            # print(w.id,count[w])
            for reg in picks[w]:
                outStr += reg + " "
                picks_left -= 1
                if picks_left == 0:
                    break
            # for loop will normally trigger else
            # if break gets called in the inner loop
            # it will skip the else
            else:
                continue
            break
        print(outStr)

    """
    Calls the map function to 'score' each region
    Keeps the top 6 and recalculates after each placement
    """

    def place_armies(self, armies):
        ranks = {}
        top_ranks = {}
        outStr = ""

        for region_id in self.map.visible_regions:
            region = self.map.regions[region_id]
            if region.occupant == self.name:
                ranks[region] = self.map.get_placement_score(
                    region, self.name, self.opponent_name, armies,self.last_move)
        # get the top 6 picks
        count = 0
        for region in sorted(ranks, key=ranks.get, reverse=True):
            top_ranks[region] = ranks[region]
            count += 1
            if count >= 6:
                break

        while armies > 0:
            for region in sorted(top_ranks, key=top_ranks.get, reverse=True):
                outStr += self.name + " place_armies " + str(region.id)
                outStr += " " + str(1) + ","
                region.armies += 1
                break
            # reevaluate
            armies -= 1
            for region in top_ranks:
                top_ranks[region] = self.map.get_placement_score(
                    region, self.name, self.opponent_name, armies)
        if outStr == "":
            print("ERROR: unplaced armies", file=sys.stderr)
            outStr += "No moves"
        print(outStr)

    """
        #Scan through all visible regions belonging to us
        #Attack the neighbor with the highest amount of enemy units
        #But only if we have more units
        #If we have no enemy neighbors
        #Scout out surrounding locations
        FIXME Optimize these loops so that the only
        access our own stored locations
    """

    def attack(self):
        regions = self.map.regions
        SAFETY_FACTOR = 1.5
        SCOUT_FORCE = 4
        threat = {}
        outStr = ""
        for region_id in self.map.visible_regions:
            region = regions[region_id]
            if region.armies <= 1:
                continue
            if regions[region_id].occupant == self.name:
                threat[region] = 0
                enemy = None
                to_scout = []
                close_targets = []
                targets = []
                safe = True
                for neighbor in region.neighbors:
                    if neighbor.occupant == self.opponent_name:
                        threat[region] += int(neighbor.armies)
                for neighbor in region.neighbors:
                    if neighbor.occupant == self.opponent_name:
                        enemy = True
                        safe = False
                        if (neighbor.super_region.is_owned(self.name)):
                            close_targets.append(neighbor)
                        else:
                            targets.append(neighbor)
                    elif neighbor.occupant == 'neutral':
                        safe = False
                        to_scout.append(neighbor)

                targets = sorted(
                    targets, key=lambda target: target.armies, reverse=True)
                close_targets = sorted(
                    close_targets,
                    key=lambda target: target.armies, reverse=True)
                if(enemy and threat[region] < region.armies):
                    final_targets = close_targets + targets
                    if region.can_attack(final_targets[0]):
                       outStr += (self.name + " attack/transfer " + region.id + " "
                       + final_targets[0].id + " " +  str(region.armies - 1)+ ",")
                    region.armies = 1

                elif (enemy):
                    targets =  close_targets + targets
                    targets = sorted(
                        targets,
                        key=lambda target: target.armies, reverse=True)
                    for targ in targets:
                        strength = targ.total_adversaries(self.name)
                        if region.can_attack(targ,strength - 2):
                            outStr += (self.name + " attack/transfer " +
                                       region.id + " " + targ.id + " " +
                                       str(int(region.armies) - 1) + ",")
                        break

                elif (not safe):
                    armies = region.armies
                    if armies <= SCOUT_FORCE and armies > 1:
                        reinforce = None
                        scores = {}
                        for neighbor in region.neighbors:
                            if neighbor.occupant == self.name:
                                scores[neighbor] = self.map.get_placement_score(
                                    neighbor, self.name,
                                    self.opponent_name,armies-1)
                        scores[region] = self.map.get_placement_score(
                            region, self.name, self.opponent_name,armies-1)
                        for reg in sorted(scores, key=scores.get,
                                          reverse=True):
                            if region == reg:
                                break
                            else:
                                reg.armies += armies - 1
                                outStr += (self.name + " attack/transfer " + region.id +
                                           " " + reg.id + " " + str(armies - 1) + ",")
                                break
                        # reinforce = region.strongest(self.name,lambda x:x.super_region==region.super_region)
                        # if not reinforce:
                        #    reinforce = region.strongest(self.name,lambda x:x.super_region==region.super_region)
                        # if reinforce:

                    else:
                        scout = sorted(to_scout, key=lambda x: int(
                            x.super_region == region.super_region), reverse=True)
                        to_send = 0
                        path = self.map.closest_enemy(region)
                        #safe_path = self.map.safest_path_to_enemy(region)
                        if  not scout[0].super_region.is_owned(self.name):
                            if len(path) and len(path) <= 3:
                                target = self.map.regions[path[0]]
                                if target.armies > (target.total_adversaries(self.name) + region.armies) or target.armies < target.total_adversaries(self.name): 
                                    outStr += (self.name + " attack/transfer " + region_id + " "
                                       + str(path[-1]) + " " + str(region.armies - 1) + ",")
                                    armies = 1
                        for i in range(len(scout)):
                            #if armies < SCOUT_FORCE:
                            #    break
                            #if i == (len(scout) - 1):
                            #to_send = armies - 1
                            #else:
                            to_send = SCOUT_FORCE
                            outStr += (self.name + " attack/transfer " +
                                       region_id + " " + scout[i].id +
                                       " " + str(to_send) + ",")
                            armies -= to_send
                            break
                # Relocate armies to regions in need
                elif safe:
                    path = self.map.closest_unowned_region(region)
                    outStr += (self.name + " attack/transfer " + region_id + " "
                               + str(path[-1]) + " " + str(region.armies - 1) + ",")
        if outStr == "":
            outStr += "No moves"
            self.last_move += 1
        else:
            self.last_move = 0
        print(outStr)

    def process_input(self, cmd):
        if cmd[0] == 'settings':
            if cmd[1] == 'your_bot':
                self.name = cmd[2]
            elif cmd[1] == 'opponent_bot':
                self.opponent_name = cmd[2]
            elif cmd[1] == 'starting_armies':
                self.start_armies = int(cmd[2])

        elif cmd[0] == 'pick_starting_regions':
            self.start_pick(cmd[2:])
        elif cmd[0] == 'setup_map':
            if cmd[1] == 'super_regions':
                # jump i by 2 because super regions are even
                # and bonuses are odd
                for i in range(2, len(cmd), 2):
                    self.map.add_super_region(cmd[i], cmd[i + 1])

            elif cmd[1] == 'regions':
                for i in range(2, len(cmd), 2):
                    self.map.add_region(cmd[i], cmd[i + 1])
            elif cmd[1] == 'neighbors':
                for i in range(2, len(cmd), 2):
                    self.map.add_neighbors(cmd[i], cmd[i + 1].split(','))
        elif cmd[0] == 'update_map':
            # clear all entries from the previous round
            self.map.visible_regions = []
            for i in range(1, len(cmd), 3):
                self.map.visible_regions.append(cmd[i])
                self.map.update_region(cmd[i], cmd[i + 1], cmd[i + 2])
            self.update_super_regions()

        elif len(cmd) == 3 and cmd[0] == 'go':
            if cmd[1] == 'place_armies':
                self.place_armies(self.start_armies)
            elif cmd[1] == "attack/transfer":
                self.attack()
        elif cmd[0] == 'opponent_moves':
            # we ignore enemy attacks on our own regions
            i = 1
            while i < len(cmd):
                name = cmd[i]
                move = cmd[i + 1]
                i += 2
                if move == 'place_armies':
                    reg = cmd[i]
                    arms = int(cmd[i + 1])
                    i += 2
                    self.map.regions[reg].armies += arms
                elif move == 'attack/transfer':
                    reg = cmd[i]
                    to_reg = cmd[i + 1]
                    arms = int(cmd[i + 2])
                    i += 3
                    if to_reg == self.opponent_name:
                        break
                    else:
                        self.map.regions[reg].armies -= arms
                        self.map.regions[to_reg].armies += arms

            # for i in range(1,len(cmd),3):
            #    self.update_moves(cmd[i],cmd[i+1])
            # FIXME TODO
            # pass
        stdout.flush()

    def run(self):
        while not stdin.closed:
            raw = stdin.readline().strip()
            if len(raw) == 0:
                continue
            else:
                eng_text = raw.split()

            self.process_input(eng_text)

if __name__ == '__main__':
    Bot().run()
