import time
import pygame
import numpy as np

from aiControl import AIControl
import global_parameter as gp

class Traffic_light:
	def __init__(self,screen_temp):
		self.screen_temp = screen_temp
		self.red = [255, 0, 0]
		self.yellow = [255, 255, 0]
		self.green = [0, 255, 0]
		self.carBlock = [
			[670, 290, 10, 100], #left
			[320, 410, 10, 100], #right
			[390, 225, 100, 10], #down
			[510, 565, 100, 10]  #up
		]
		self.persBlock = [
			[620, 220, 10, 70, 1], #left
			[620, 515, 10, 70, 1],
			[365, 220, 10, 70, 2], #right
			[365, 515, 10, 70, 2],
			[315, 270, 70, 10, -2], #down
			[615, 270, 70, 10, -2],
			[315, 515, 70, 10, -1], #up
			[615, 515, 70, 10, -1]
		]
		self.timer = 0
		self.horizontal = True #哪个方向信号管制
		self.aiC = AIControl() # instance
		self.yorder = False # 黄灯变化
		self.ytimer = 0
		self.result = True

	def redLight(self,rl,pl):
		# 表示红灯,添加车辆/行人红灯坐标
		for r in rl:
			pygame.draw.rect(self.screen_temp, self.red, self.carBlock[r], 0)
		for c in rl:
			self.car_gps = np.append(self.car_gps, [
				0, # 方向type
				self.carBlock[c][0],
				self.carBlock[c][1],
				self.carBlock[c][0] + self.carBlock[c][2],
				self.carBlock[c][1] + self.carBlock[c][3],
				0 # 速度0
			])
		for p in pl:
			self.pers_gps = np.append(self.pers_gps, [
				self.persBlock[p][4],
				self.persBlock[p][0],
				self.persBlock[p][1],
				self.persBlock[p][0] + self.persBlock[p][2],
				self.persBlock[p][1] + self.persBlock[p][3],
			])

	def yellowLight(self,yl,pl):
		# 表示黄灯,添加车辆/行人黄灯坐标
		for y in yl:
			pygame.draw.rect(self.screen_temp, self.yellow, self.carBlock[y], 0)
		for c in yl:
			self.car_gps = np.append(self.car_gps, [
				0, # 方向type
				self.carBlock[c][0],
				self.carBlock[c][1],
				self.carBlock[c][0] + self.carBlock[c][2],
				self.carBlock[c][1] + self.carBlock[c][3],
				0 # 速度0
			])
		pl = list(set(list(range(8))) ^ set(pl))
		for p in pl :
			self.pers_gps = np.append(self.pers_gps, [
				self.persBlock[p][4],
				self.persBlock[p][0],
				self.persBlock[p][1],
				self.persBlock[p][0] + self.persBlock[p][2],
				self.persBlock[p][1] + self.persBlock[p][3],
			])

	def blueLight(self,bl):
		# 表示绿灯
		for i in bl:
			pygame.draw.rect(self.screen_temp, self.green, self.carBlock[i], 0)

	def timeChange(self,car_gps,pers_gps):
		''' 固定时差改变信号灯 '''
		self.car_gps = car_gps
		self.pers_gps = pers_gps
		# 如果计时器为0,则带入时间戳
		if self.timer == 0:
			self.timer = time.time()
		elif (self.timer + gp.RED_TIME) <= time.time():
			# 固定时长改变红绿灯
			self.horizontal = bool(1 - self.horizontal) #布尔值取反
			self.timer = time.time() #新的计时
		# 判定水平或者垂直方向通行禁止
		if self.horizontal:
			# 设定需要设置的红绿灯情报,需要添加到车辆/行人列表中的值
			bl = list(range(2,4))
			rl = list(range(2))
			pl = list(range(4))
		else:
			bl = list(range(2))
			rl = list(range(2,4))
			pl = list(range(4,8))
		
		# 根据时间轴决定表示的信号灯
		# 垂直方向绿/黄灯制御
		if (self.timer + gp.RED_TIME - gp.YELLOW_TIME) >= time.time():
			self.blueLight(bl)
		else:
			self.yellowLight(bl,pl)
		# 水平方向信号红灯制御
		self.redLight(rl,pl)

		return self.car_gps,self.pers_gps

	def aiChange(self,car_gps,pers_gps):
		''' 根据情况改变信号灯 '''
		# 将车辆列表,行人列表,时间戳传入AIControl类
		self.car_gps = car_gps
		self.pers_gps = pers_gps

		if self.timer == 0:
			self.timer = time.time()

		# 如果进入变灯流程,则不进行判定
		if not(self.yorder):
			self.aiC.list_process(self.car_gps,self.pers_gps)
			self.result = self.aiC.aiControl(self.timer,self.horizontal)
			# 如果只能判定与现有信号不同,则进入变灯流程
			if self.result != self.horizontal:
				# 如果判断结果和现状不同,则更改yorder
				self.yorder = True
				self.ytimer = time.time()

		if self.horizontal:
			# 设定需要设置的红绿灯情报,需要添加到车辆/行人列表中的值
			bl = list(range(2,4))
			rl = list(range(2))
			pl = list(range(4))
		else:
			bl = list(range(2))
			rl = list(range(2,4))
			pl = list(range(4,8))
		
		# 判定是黄灯或者绿灯
		if self.yorder:
			self.yellowLight(bl,pl)
			if time.time() >= self.ytimer + gp.YELLOW_TIME:
				# 根据黄灯时长,判定变灯流程是否结束
				self.yorder = False
				self.horizontal = self.result
				self.timer = time.time()
		else:
			self.blueLight(bl)
			
		# 水平方向信号红灯制御
		self.redLight(rl,pl)

		return self.car_gps,self.pers_gps

