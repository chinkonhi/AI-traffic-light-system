import numpy as np

import global_parameter as gp

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

