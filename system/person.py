import pygame,random

class Person:
	def __init__(self,screen_temp,road):
		if road[0] > 0:
			self.x = road[1]
			self.y = random.choice(range(road[2],road[2]+41))
		else:
			self.x = random.choice(range(road[1],road[1]+41))
			self.y = road[2]
		self.type = road[0]
		self.screen_temp = screen_temp
		self.image = \
		pygame.image.load("../img/p"+str(random.choice(range(1,5)))+"_"+str(road[0])+".png")
	
	def display(self):
		self.screen_temp.blit(self.image, (self.x, self.y))

	def delete(self):
		if ((self.type == 1) & (self.x <= -20)):
			return True
		elif ((self.type == 2) & (self.x >= 920)):
			return True
		elif ((self.type == -2) & (self.y >= 780)):
			return True
		elif ((self.type == -1) & (self.y <= -20)):
			return True

