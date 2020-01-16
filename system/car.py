import pygame

import global_parameter as gp

class Car:
	'''控制车辆类'''
	def __init__(self,screen_temp,road):
		self.x = road[0]
		self.y = road[1]
		self.type = road[3]
		self.speed = gp.CAR_INITIAL # 初始速度为0
		self.screen_temp = screen_temp
		self.image = pygame.image.load("../img/"+road[2]+".png")			

	def display(self):
		self.screen_temp.blit(self.image,(self.x,self.y))

	def delete(self):
		if ((self.type == 1) & (self.x <= -100)):
			return True
		elif ((self.type == 2) & (self.x >= 1000)):
			return True
		elif ((self.type == -2) & (self.y >= 950)):
			return True
		elif ((self.type == -1) & (self.y <= -100)):
			return True