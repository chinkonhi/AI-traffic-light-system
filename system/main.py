#交通系统模拟
#导入模块
import pygame
from pygame.locals import * #pyganme使用的各种常量
import time,random
import sys
import numpy as np

#导入全局变量global
import global_parameter as gp
from traffic_light import Traffic_light
from car import Car
from car_control import Car_control
from person import Person
from pers_control import Pers_control


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

# 计算表示2种模式下的等待时长
