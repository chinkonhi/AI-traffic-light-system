import global_parameter as gp
import numpy as np

class AIControl:
	def __init__(self,horizontal):
		self.horizontal = horizontal

	def list_process(self,carlist,perlist):
		# 处理列表,取得type,x,y
		for ls in [carlist,perlist]:
			ls[ls[:,0]==2,1] = ls[ls[:,0]==2,3]
			ls[ls[:,0]==2,2] = ls[ls[:,0]==2,4]
			ls[ls[:,0]==-2,1] = ls[ls[:,0]==-2,3]
			ls[ls[:,0]==-2,2] = ls[ls[:,0]==-2,4]

		carlist = np.delete(carlist, range(3,6), axis = 1)
		perlist = np.delete(perlist, range(3,5), axis = 1)

		# 筛选出可扫描范围内的坐标900,756
		
		carlist = carlist[(carlist[:,1]>0)&(carlist[:,1]<900)&(carlist[:,2]>0)&(carlist[:,2]<756)]
		perlist = perlist[(perlist[:,1]>0)&(perlist[:,1]<900)&(perlist[:,2]>0)&(perlist[:,2]<756)]

		self.carlist = carlist
		self.perlist = perlist

	def aiControl(self):
		# 收取到的列表进行计算做出判断
		# 车/人系数 * 等待时长 * 数量
		# 不是整体,而是以各个方向,做出判断
		# 4个车道,4个人行道
		# 系数由当前路面容量极限值决定
		pass