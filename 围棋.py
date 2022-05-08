from scene import Scene
import taichi as ti
from taichi.math import *
v场景 = Scene(voxel_edges = 0, exposure = 1)
v场景.set_floor(-2/64, (0.1, 0.2, 0.1))
v场景.set_background_color((0.5, 0.5, 0.9))
# v场景.set_directional_light((0, 1, 0), 0.1, (0.5, 0.5, 0.5))
v棋谱 = """0000000000000000000\
0020000022022011100\
0202100211012121220\
0021000000012122120\
0110000000122121000\
0212000001000122200\
0122000002110010000\
0010100000002222000\
0000000000112110000\
0000002020001201000\
0000200002210021000\
0020001002110201000\
0000200000210021000\
0011112121210021000\
0212020222012122100\
0111220212210211100\
0212022112122021000\
0000111001100002100\
0000000000000000000"""
v棋谱 = list(int(x) for x in v棋谱)
c黑棋颜色 = vec3(0.1, 0.1, 0.1)
c白棋颜色 = vec3(1, 1, 1)
@ti.kernel
def f初始化棋盘():
	#棋盘
	for x, y, z in ti.ndrange((-40, 41), (-2, 0), (-40, 41)):	#底座
		c = vec3(ti.random()*0.1 + 0.9, ti.random()*0.1 + 0.4, ti.random()*0.1)
		v场景.set_voxel(vec3(x, y, z), 1, c)
	for i in range(19):	#网格线
		a = (i-9)*4
		for j in range(-36, 37):
			v场景.set_voxel(vec3(a, -1, j), 1, vec3(0.1, 0.1, 0.1))
			v场景.set_voxel(vec3(j, -1, a), 1, vec3(0.1, 0.1, 0.1))
@ti.kernel
def f落子(x: int, y: int, c: int):
	#计算棋子在空间中的坐标
	x1, y1 = (x-9)*4, (y-9)*4
	c1 = c黑棋颜色 if c == 1 else c白棋颜色
	#生成棋子
	for i, j in ti.ndrange((-1, 2), (-1, 2)):
		v场景.set_voxel(vec3(x1+i, 0, y1+j), 2, c1)
	v场景.set_voxel(vec3(x1, 1, y1), 2, c1)	
f初始化棋盘()
for i in range(19*19):
	v棋子 = v棋谱[i]
	if v棋子 != 0:
		x, y = i % 19, i // 19
		f落子(x, y, v棋子)
v场景.finish()