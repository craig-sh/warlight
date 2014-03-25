from sys import stdin,stdout
from map import Map
class Bot(object):
    def __init__(self):
        self.name = ""
        self.map = Map()
        self.start_armies = 0
        self.opponent_name = ""

    """
    Tries and group picks into the same super region
    Consider evaluating the distances between all picks as well
    """
    def start_pick(self,regions):
        count = {}
        picks = {}
        picks_left = 6
        for region in regions:
            super_region = self.map.regions[region].super_region
            if not super_region in count:
                count[super_region] = 0
                picks[super_region] = []
            count[super_region] += 1 + super_region.bonus * 0.1
            picks[super_region].append(region)
        outStr = ""
        for w in sorted(count,key=count.get,reverse=True):
            #print(w,count[w])
            for reg in picks[w]:
                outStr += reg + " "
                picks_left -= 1
                if picks_left == 0:
                    break
            #for loop will normally trigger else
            #if break gets called in the inner loop
            #it will skip the else
            else:
                continue
            break
        print outStr

    """
    #Place armies in regions that are connected
    #to enemy regions so that they have armies
    #equal to the number that the enemy does
    #then place the rest of the armies
    #in regions that have adjacent terrotories that
    #are free
    FIXME :optimize loops so that we store our own locations
    """
    def place_armies(self,armies):
        threat = {}
        armies_left = armies
        regions = self.map.regions
        outStr = ""
        SAFETY_FACTOR = 1.5
        for region_id in self.map.visible_regions:
            if regions[region_id].occupant ==  self.name:
                for neighbor in regions[region_id].neighbors:
                    if neighbor.occupant == self.opponent_name:
                        if not region_id in threat:
                            threat[region_id] = 0
                        threat[region_id] += int(neighbor.armies)
        for region_id in sorted(threat,key=threat.get,reverse=True):
            if not armies_left:
                break
            if threat[region_id] > regions[region_id].armies * SAFETY_FACTOR:
                outStr += self.name + " place_armies " + str(region_id)
                placed_count = 0
                while armies_left > 0:
                    placed_count += 1
                    armies_left -= 1
                outStr += " " + str(placed_count) + ","

        for region_id in self.map.visible_regions:
            if armies_left  < 2:
                break
            if regions[region_id].occupant == self.name:
                for neighbor in regions[region_id].neighbors:
                    if armies_left  < 2:
                        break
                    if neighbor.occupant == 'neutral':
                        armies_left -= 1
                        outStr += self.name + " place_armies " + str(region_id)
                        outStr += " " + str(1) +","


        print outStr
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
        outStr = ""
        SAFETY_FACTOR = 1.5
        SCOUT_FORCE = 3
        for region_id in self.map.visible_regions:
            if regions[region_id].occupant ==  self.name:
                target = None
                to_scout = []
                for neighbor in regions[region_id].neighbors:
                    if neighbor.occupant == self.opponent_name:
                        if target == None or neighbor.armies > target.armies:
                            target = neighbor
                    elif neighbor.occupant == 'neutral':
                        to_scout.append(neighbor)
###################ATTACK ADJACENT ARMIES###############################################
                if target and target.armies * SAFETY_FACTOR < regions[region_id].armies:
                    outStr += (self.name + " attack/transfer " + region_id + " "
                            + target.id + " " +  str(regions[region_id].armies - 1)+ ",")
##########################################################################################
            #FIXME- if we have a region that is surrounded by friendly regions
            #       we need to send all the armies from that regions to reinforce
            #       the closest region in danger
##########################SCOUTING###############################################
                elif target == None and len(to_scout):
                    armies = regions[region_id].armies
                    #Send two armies to each region and the remaining to the last unscouted region
                    #This will leave only one army in the current region
                    for i in range(len(to_scout)):
                        if armies <= SCOUT_FORCE:
                            break
                        if i == (len(to_scout) - 1):
                            to_send = armies - 1
                        else:
                            to_send = SCOUT_FORCE
                        outStr += (self.name + " attack/transfer " + region_id +
                                 " " +  to_scout[i].id + " " +str(to_send) + ",")
                        armies -= to_send
        if outStr == "":
            outStr += "No moves"
        print outStr

    def process_input(self,cmd):
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
                #jump i by 2 because super regions are even
                #and bonuses are odd
                for i in range(2,len(cmd),2):
                    self.map.add_super_region(cmd[i],cmd[i+1])

            elif cmd[1] == 'regions':
                for i in range(2,len(cmd),2):
                    self.map.add_region(cmd[i],cmd[i+1])
            elif cmd[1] == 'neighbors':
                for i in range(2,len(cmd),2):
                    self.map.add_neighbors(cmd[i],cmd[i+1].split(','))
        elif cmd[0] == 'update_map':
            #clear all entries from the previous round
            self.map.visible_regions = []
            for i in range(1,len(cmd),3):
                self.map.visible_regions.append(cmd[i])
                self.map.update_region(cmd[i],cmd[i+1],cmd[i+2])

        elif len(cmd) == 3 and cmd[0] == 'go':
            if cmd[1] == 'place_armies':
                self.place_armies(self.start_armies)
            elif cmd[1] == "attack/transfer":
                self.attack()
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