import global_parameter as gp
import numpy as np
import time

class AIControl:
	def __init__(self,horizontal):
		self.horizontal = horizontal
		self.change_time = 0

	def list_process(self,clist,plist):
		# 处理列表,取得type,x,y
		
		carlist = clist.copy()
		perlist = plist.copy()

		for ls in [carlist,perlist]:
			ls[ls[:,0]==2,1] = ls[ls[:,0]==2,3]
			ls[ls[:,0]==2,2] = ls[ls[:,0]==2,4]
			ls[ls[:,0]==-2,1] = ls[ls[:,0]==-2,3]
			ls[ls[:,0]==-2,2] = ls[ls[:,0]==-2,4]

		carlist = np.delete(carlist, range(3,6), axis = 1)
		perlist = np.delete(perlist, range(3,5), axis = 1)

		# 筛选出可扫描范围内的坐标900,756内的,信号前的坐标
		# 信号坐标参照main
		carlist = carlist[
			(carlist[:,1] > 0)
			&(carlist[:,1] < 900)
			&(carlist[:,2] > 0)
			&(carlist[:,2] < 756)
		]
		#carlist = carlist[
		#	(carlist[:,0] == 1)&(carlist[:,1] > 670)
		#	&(carlist[:,0] == 2 )&(carlist[:,1] < 320)
		#	&(carlist[:,0] == -1)&(carlist[:,2] > 565)
		#	&(carlist[:,0] == -2)&(carlist[:,2] < 225)
		#]
		perlist = perlist[
			(perlist[:,1] > 0)
			&(perlist[:,1] < 900)
			&(perlist[:,2] > 0)
			&(perlist[:,2] < 756)
		]
		#perlist = perlist[
		#	(perlist[:,0] == 1)&(perlist[:,1] > 620)
		#	&(perlist[:,0] == 2)&(perlist[:,1] < 365)
		#	&(perlist[:,0] == -1)&(perlist[:,2] > 515)
		#	&(perlist[:,0] == -2)&(perlist[:,2] < 270)
		#]

		# 抽出有效范围内的坐标的数量,放入新列表
		self.carCount = np.array([
			carlist[carlist[:,0] == 1].shape[0], #left
			carlist[carlist[:,0] == 2].shape[0], #right
			carlist[carlist[:,0] == -1].shape[0], #up
			carlist[carlist[:,0] == -2].shape[0] #down
		])
		self.perCount = np.array([
			perlist[(perlist[:,0] == 1)&(perlist[:,2] < 350)].shape[0],
			perlist[(perlist[:,0] == 1)&(perlist[:,2] > 350)].shape[0],
			perlist[(perlist[:,0] == 2)&(perlist[:,2] < 350)].shape[0],
			perlist[(perlist[:,0] == 2)&(perlist[:,2] > 350)].shape[0],
			perlist[(perlist[:,0] == -1)&(perlist[:,1] < 450)].shape[0],
			perlist[(perlist[:,0] == -1)&(perlist[:,1] > 450)].shape[0],
			perlist[(perlist[:,0] == -2)&(perlist[:,1] < 450)].shape[0],
			perlist[(perlist[:,0] == -2)&(perlist[:,1] > 450)].shape[0]
		])
		#print(self.carCount)
		#print(self.perCount)

	def aiControl(self,change_time):
		# 记录当前信号状况的时间戳
		self.change_time = change_time

		# 计算负荷值(数量*等待时长*基数)
		if self.horizontal: # 水平方向红灯,垂直方向通行
			# car
			self.carCount[[0,1]] = \
			self.carCount[[0,1]] * (int)((time.time()-self.change_time)/gp.YELLOW_TIME) * gp.C_WAITVALUE
			self.carCount[[2,3]] = self.carCount[[2,3]] * gp.C_WAITVALUE
			# person
			self.perCount[range(0,4)] = \
			self.perCount[range(0,4)] * (int)((time.time()-self.change_time)/gp.YELLOW_TIME) * gp.P_WAITVALUE
			self.perCount[range(4,8)] = self.perCount[range(4,8)] * gp.P_WAITVALUE
		else:
			# car
			self.carCount[[2,3]] = \
			self.carCount[[2,3]] * (int)((time.time()-self.change_time)/gp.YELLOW_TIME) * gp.C_WAITVALUE
			self.carCount[[0,1]] = self.carCount[[0,1]] * gp.C_WAITVALUE
			# person
			self.perCount[range(4,8)] = \
			self.perCount[range(4,8)] * (int)((time.time()-self.change_time)/gp.YELLOW_TIME) * gp.P_WAITVALUE
			self.perCount[range(0,4)] = self.perCount[range(0,4)] * gp.P_WAITVALUE
		
		# 排序列表,取出最大值,根据最大值控制信号
		result = np.argmax(np.hstack([self.carCount,self.perCount]))
		#print(self.carCount)
		#print(self.perCount)
		
		if result in [0,1,4,5,6,7]:
			# 水平方向有最大值
			#print("水平")
			#print(np.hstack([self.carCount,self.perCount])[result])
			return True
		else:
			#print("垂直")
			#print(np.hstack([self.carCount,self.perCount])[result])
			return False