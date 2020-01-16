#交通系统模拟
#导入模块
import pygame
from pygame.locals import * #pyganme使用的各种常量
import time,random
import sys
import numpy as np
#导入全局变量global
import global_parameter as gp
from aiControl import AIControl

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


class Car_control:
	def __init__(self):
		self.car_gps = np.array([], dtype=int)
		self.crash = np.array([], dtype=int)

	def gpsCreate(self, clist):
		#列表生成器,放入所有车的现坐标
		self.clist = clist
		for cMsg in self.clist:
			self.car_gps = np.append(self.car_gps, [cMsg.type, cMsg.x, cMsg.y, 0, 0, cMsg.speed])
		self.car_gps = self.car_gps.reshape(-1,6)
		
		#创建所有车辆的坐标面
		self.car_gps[self.car_gps[:,0]>0, 3] = \
			self.car_gps[self.car_gps[:,0]>0, 1] + gp.CAR_HEIGHT
		self.car_gps[self.car_gps[:,0]>0, 4] = \
			self.car_gps[self.car_gps[:,0]>0, 2] + gp.CAR_WIDTH
		self.car_gps[self.car_gps[:,0]<0, 3] = \
			self.car_gps[self.car_gps[:,0]<0, 1] + gp.CAR_WIDTH
		self.car_gps[self.car_gps[:,0]<0, 4] = \
			self.car_gps[self.car_gps[:,0]<0, 2] + gp.CAR_HEIGHT
		
		#创建所有车辆的碰撞检测点(2个)
		self.crash = self.car_gps.copy()
		self.crash[self.crash[:,0]==1] += [0, -gp.CAR_SPEED, 0, -(gp.CAR_HEIGHT+gp.CAR_SPEED), 0, 0]
		self.crash[self.crash[:,0]==2] += [0, (gp.CAR_HEIGHT+gp.CAR_SPEED), 0, gp.CAR_SPEED, 0, 0]
		self.crash[self.crash[:,0]==-2] += [0, 0, (gp.CAR_HEIGHT+gp.CAR_SPEED), 0, gp.CAR_SPEED, 0]
		self.crash[self.crash[:,0]==-1] += [0, 0, -gp.CAR_SPEED, 0, -(gp.CAR_HEIGHT+gp.CAR_SPEED), 0]
		self.crash = np.delete(self.crash, 5, axis=1)
		self.crash = np.delete(self.crash, 0, axis=1)
		
		return self.car_gps

	def crashCheck(self,tL_car_gps):
		''' 判断是否可以前进 '''
		self.car_gps = tL_car_gps.reshape(-1,6)
		ind = 0
		for cs in self.crash: 
		# 遍历所有车辆的的碰撞点(不包含信号灯坐标),如果没有和已被占用坐标冲撞,则前行
			if not(
				any(
					(cs[0]>=self.car_gps[:,1])&
					(cs[0]<=self.car_gps[:,3])&
					(cs[1]>=self.car_gps[:,2])&
					(cs[1]<=self.car_gps[:,4])
				)|\
				any(
					(cs[2]>=self.car_gps[:,1])&
					(cs[2]<=self.car_gps[:,3])&
					(cs[3]>=self.car_gps[:,2])&
					(cs[3]<=self.car_gps[:,4])
				)
			):
				if self.car_gps[ind,0] > 0:
				# 根据方向(type)使车前行
					if abs(self.car_gps[ind,0]) == 1:
						self.clist[ind].x -= self.car_gps[ind, 5] # 根据速度进行移动
						self.car_gps[ind] += [0, -self.car_gps[ind, 5], 0, -self.car_gps[ind, 5], 0, 0]
					else:
						self.clist[ind].x += self.car_gps[ind, 5]
						self.car_gps[ind] += [0, self.car_gps[ind, 5], 0, self.car_gps[ind, 5], 0, 0]
				else:
					if abs(self.car_gps[ind,0]) == 1:
						self.clist[ind].y -= self.car_gps[ind, 5]
						self.car_gps[ind] += [0, 0, -self.car_gps[ind, 5], 0, -self.car_gps[ind, 5], 0]
					else:
						self.clist[ind].y += self.car_gps[ind, 5]
						self.car_gps[ind] += [0, 0, self.car_gps[ind, 5], 0, self.car_gps[ind, 5], 0]
				# 加速
				if self.clist[ind].speed < gp.CAR_SPEED:
					self.clist[ind].speed += gp.CAR_ACCELERATE
				else :
					self.clist[ind].speed = gp.CAR_SPEED
			else: # 如果监测到碰撞,则将车辆速度设置为初始速度0
				self.clist[ind].speed = gp.CAR_INITIAL

			ind += 1

		return self.clist

	def reset(self):
		self.car_gps = np.array([], dtype=int)
		self.crash = np.array([], dtype=int)


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


class Pers_control:
	def __init__(self):
		self.pers_gps = np.array([], dtype=int)
		self.pers_crash = np.array([], dtype=int)

	def gpsCreate(self,plist):
		self.plist = plist
		for pMsg in self.plist:
			self.pers_gps = np.append(self.pers_gps, [pMsg.type, pMsg.x, pMsg.y, 0, 0])
		self.pers_gps = self.pers_gps.reshape(-1,5)
		
		#复制self.pers_gps的前3列,创建pers_crash用于放置前进坐标点
		self.pers_crash = self.pers_gps[:,range(3)].copy()
		self.pers_crash[self.pers_crash[:,0]==1] += [0, -gp.PERS_SPEED, 0]
		self.pers_crash[self.pers_crash[:,0]==2] += [0, gp.PERS_SPEED, 0]
		self.pers_crash[self.pers_crash[:,0]==-2] += [0, 0, gp.PERS_SPEED]
		self.pers_crash[self.pers_crash[:,0]==-1] += [0, 0, -gp.PERS_SPEED]
		
		#建立每个人的坐标空间
		self.pers_gps[self.pers_gps[:,0]>0, 3] = \
			self.pers_gps[self.pers_gps[:,0]>0, 1] + gp.PERS_HEIGHT
		self.pers_gps[self.pers_gps[:,0]>0, 4] = \
			self.pers_gps[self.pers_gps[:,0]>0, 2] + gp.PERS_WIDTH
		self.pers_gps[self.pers_gps[:,0]<0, 3] = \
			self.pers_gps[self.pers_gps[:,0]<0, 1] + gp.PERS_WIDTH
		self.pers_gps[self.pers_gps[:,0]<0, 4] = \
			self.pers_gps[self.pers_gps[:,0]<0, 2] + gp.PERS_HEIGHT

		return self.pers_gps

	def crashCheck(self, tL_pers_gps):
		tL_pers_gps = tL_pers_gps.reshape(-1,5)
		ind = 0
		for p_c in self.pers_crash:
			#碰撞检测
			if not(any(
				(p_c[0]==tL_pers_gps[:,0])&
				(p_c[1]>tL_pers_gps[:,1])&(p_c[1]<tL_pers_gps[:,3])&
				(p_c[2]>tL_pers_gps[:,2])&(p_c[2]<tL_pers_gps[:,4])
			)):
				if p_c[0]>0:
					if abs(p_c[0])==1:
						self.plist[ind].x -= gp.PERS_SPEED
						tL_pers_gps[ind] += [0, -gp.PERS_SPEED, 0, -gp.PERS_SPEED, 0]
					else:
						self.plist[ind].x += gp.PERS_SPEED
						tL_pers_gps[ind] += [0, gp.PERS_SPEED, 0, gp.PERS_SPEED, 0]
				else:
					if abs(p_c[0])==1:
						self.plist[ind].y -= gp.PERS_SPEED
						tL_pers_gps[ind] += [0, 0, -gp.PERS_SPEED, 0, -gp.PERS_SPEED]
					else:
						self.plist[ind].y += gp.PERS_SPEED
						tL_pers_gps[ind] += [0, 0, gp.PERS_SPEED, 0, gp.PERS_SPEED]
			ind += 1

		return self.plist

	def reset(self):
		self.pers_gps = np.array([], dtype=int)		


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


def sideMenu(screen):
	''' 生成侧边目录 '''
	screen.blit(pygame.image.load("../img/sideBack.png"),(0,0))
	screen.blit(pygame.image.load("../img/start.jpg"),(10,60))
	screen.blit(pygame.image.load("../img/suspend.jpg"),(10,120))
	screen.blit(pygame.image.load("../img/時差式.jpg"),(10,200))
	screen.blit(pygame.image.load("../img/知能式.jpg"),(10,260))
	screen.blit(pygame.image.load("../img/+.jpg"),(7,340))
	screen.blit(pygame.image.load("../img/-.jpg"),(53,340))

def textShow(screen,text_value,text_frequency):
	# 通行频度
	screen.blit(text_frequency,(0,5))
	# 信号类型
	screen.blit(text_value,(0,24))

def frequentControl(render_frequency,frequency,plusminus):
	''' 控制车辆行人出现频度 '''
	frequencies = np.array([gp.HIGH_FREQUENT,gp.MIDDLE_FREQUENT,gp.LOW_FREQUENT]) #15 30 50
	flist = ["High","Middle","Low"]

	if plusminus > 0:
		# 提升频率
		if frequencies[frequency>frequencies].size != 0:
			frequency = frequencies[frequency>frequencies][-1]
			index = np.argwhere(frequencies == frequency)[0,0]
			render_frequency = flist[index]
	else:
		# 降低频率
		if frequencies[frequency<frequencies].size != 0: 
			frequency = frequencies[frequency<frequencies][0]
			index = np.argwhere(frequencies == frequency)[0,0]
			render_frequency = flist[index]

	print(render_frequency)
	return render_frequency,frequency

#创建主窗口
def main():
	'''主程序执行函数'''
	#初始化
	pygame.init()

	#创建窗口:set_mode(分辨率=(0,0),标志=0,深度=0)
	screen = pygame.display.set_mode((900,756),0,0)

	#设置窗口标题
	pygame.display.set_caption("交通制御システム")

	#加载图像,返回图片对象
	background = pygame.image.load("../img/cross1.jpg")

	#设置车辆行人频度变数
	frequency = gp.MIDDLE_FREQUENT

	#flag
	flag = 0
	pattern = 0

	#车辆,人列表
	carlist = []
	personlist = []

	#实例化
	carControl = Car_control()
	persControl = Pers_control()
	trafficLight = Traffic_light(screen)

	#各个车道的初始位置(x坐标,y坐标,画像,方向)
	road_shape = [
		[1000,295,'b_l',1],
		[1000,345,'b_l',1], #left
		[-100,410,'b_r',2],
		[-100,460,'b_r',2],#right
		[390,-200,'b_d',-2],
		[450,-200,'b_d',-2],#down
		[510,850,'b_u',-1],
		[570,850,'b_u',-1],#up
	]
	#行人的初始情报
	pers_shape = [
		[1,920,225],#265
		[1,920,520],#560
		[2,-20,225],
		[2,-20,520],
		[-2,320,-20],#360
		[-2,620,-20],#660
		[-1,320,780],
		[-1,620,780]
	]

	#创建文字对象
	text = pygame.font.Font("../font/YuGothM.ttc",14)
	text_value = text.render("",1,(255,0,0))
	text_frequency = text.render("通行量：Middle",1,(255,0,0))
	render_frequency = "Middle"

	#开始前预处理
	screen.blit(background,(100,0))
	sideMenu(screen)
	pygame.display.flip()

	#系统主循环
	while True: #死循环保持窗口一直显示
		for event in pygame.event.get(): #遍历所有事件
			if event.type == QUIT: #如果点击关闭窗口,则退出
				sys.exit()
			elif event.type == pygame.MOUSEBUTTONDOWN:
				# 侧边栏按钮控制
				pos = pygame.mouse.get_pos()
				mouse_x = pos[0]
				mouse_y = pos[1]

				if ((10<mouse_x<90) & (60<mouse_y<100)):#开始
					flag = 1

				elif ((10<mouse_x<90) & (120<mouse_y<160)):#暂停
					flag = 0

				elif ((10<mouse_x<90) & (200<mouse_y<240)):#时差式
					pattern = 1
					text_value = text.render("時差式",1,(255,0,0))

				elif ((10<mouse_x<90) & (260<mouse_y<300)):#知能式
					pattern = 2
					text_value = text.render("知能式",1,(255,0,0))

				elif ((7<mouse_x<47) & (340<mouse_y<380)): #+
					render_frequency,frequency = frequentControl(render_frequency,frequency,1)
					text_frequency = text.render("通行量："+render_frequency,1,(255,0,0))

				elif ((53<mouse_x<93) & (340<mouse_y<380)): #-
					render_frequency,frequency = frequentControl(render_frequency,frequency,-1)
					text_frequency = text.render("通行量："+render_frequency,1,(255,0,0))

		if flag == 1:
			#绘制图像
			screen.blit(background,(100,0))

			#随机绘制车辆
			#控制车辆出现频度
			if random.choice(range(frequency)) == 1:
				#控制车辆的车道
				road = random.choice(range(len(road_shape))) #根据车道决定初始坐标
				carlist.append(Car(screen,road_shape[road]))
			if random.choice(range(frequency)) == 1:
				#控制人出现
				style = random.choice(range(len(pers_shape)))
				personlist.append(Person(screen,pers_shape[style]))

			car_gps = carControl.gpsCreate(carlist)
			pers_gps = persControl.gpsCreate(personlist)

			#将红绿灯信息写入,并执行
			if pattern == 1:#时差式
				tL_car_gps,tL_pers_gps = trafficLight.timeChange(car_gps,pers_gps)
			elif pattern == 2:#知能式
				tL_car_gps,tL_pers_gps = trafficLight.aiChange(car_gps,pers_gps)
			else:
				tL_car_gps = car_gps
				tL_pers_gps = pers_gps

			#判断可否前进
			carlist = carControl.crashCheck(tL_car_gps)
			for car in carlist:
				car.display()
				if car.delete():
					carlist.remove(car) #消除车

			plist = persControl.crashCheck(tL_pers_gps)
			for p in plist:
				p.display()
				if p.delete():
					personlist.remove(p) #消除车
			
			carControl.reset()
			persControl.reset()

			#刷新画面
			sideMenu(screen)
			textShow(screen,text_value,text_frequency)
			pygame.display.update()

		#定时显示
		time.sleep(0.04)

	pygame.quit() #退出pygame
		

if __name__ == "__main__":
	main()


#1.频度调整的按钮和机能
#2.将类分离为单独文件
#3.类似Future的同步处理
#4.计算表示2种模式下的等待时长
