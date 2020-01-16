import numpy as np

import global_parameter as gp

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

