from sys import stdin,stdout
from map import Map
class Bot(object):
	def __init__(self):
		self.name = ""
		self.map = Map()

	def start_pick(self,regions):
		count = {}
		picks = {}
		picks_left = 6
	 	for region in regions:
	 		super_region = self.map.regions[region].super_region
	 		if not super_region in count:
	 			count[super_region] = 0
	 			picks[super_region] = []
	 		count[super_region] += self.map.super_regions[super_region].bonus
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

	def process_input(self,cmd):
		if cmd[0] == 'settings':
			if cmd[1] == 'your_bot':
				self.name = cmd[2]
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

		elif len(cmd) == 3 and cmd[0] == 'go':
			out = ""
			if cmd[1] == 'place_armies':
				for i in range(1,42):
					out += self.name + " place_armies " \
					+ str(i) + " 1,"
			elif cmd[1] == "attack/transfer":
				for i in range(1,42):
					out += self.name + " attack/transfer " \
					+ str(i) + " " + str(i+1) + " 1,"
			print(out)
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