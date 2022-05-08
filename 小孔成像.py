from scene import Scene
import taichi as ti
from taichi.math import *
v场景 = Scene(voxel_edges = 0, exposure = 1)
v场景.set_floor(-1, (1, 1, 1))
R = 8
N = 32
@ti.func
def lerp(a, b, t):
	return a + (b - a) * t
@ti.func
def rainbow(h: float):
	h = h * 6	#范围[0, 6],红橙黄绿青蓝紫
	r, g, b = 0.0, 0.0, 0.0
	if h < 1: r, g = 1, lerp(0, 0.5, h)	#红->橙
	elif h < 2:	r, g = 1, lerp(0.5, 1, h - 1)	#橙->黄
	elif h < 3:	r, g = lerp(1, 0, h - 2), 1	#黄->绿
	elif h < 4:	g, b = 1, lerp(0, 1, h - 3)	#绿->青
	elif h < 5:	g, b = lerp(1, 0, h - 4), 1	#青->蓝
	elif h < 6:	b, r = 1, lerp(0, 1, h - 5)	#蓝->紫
	else: b, r = lerp(1, 0, h - 6), 1	#紫->红
	return vec3(r, g, b)
@ti.kernel
def f初始化():
	#发光箭头
	for i, j in ti.ndrange((-4, 5), (-32, 16)):
		c = rainbow((j + N) / (2*N))
		v场景.set_voxel(vec3(i, j, 63), 2, c)
	for i, j in ti.ndrange(16, 16):
		if i <= 15 - j:
			y = j + 16
			c = rainbow((y + N) / (2*N))
			v场景.set_voxel(vec3(i, y, 63), 2, c)
			v场景.set_voxel(vec3(-i, y, 63), 2, c)
	#中间墙
	for i, j in ti.ndrange((-32, 32), (-32, 32)):
		v场景.set_voxel(vec3(i, j, 0), 1, vec3(0.5, 0.5, 0.5))
	for i, j in ti.ndrange((-R, R+1), (-R, R+1)):	#中间挖个洞
		if i*i+j*j < R*R:
			v场景.set_voxel(vec3(i, j, 0), 0, vec3(0.5, 0.5, 0.5))
	#背后墙
	for i, j in ti.ndrange((-32, 32), (-32, 32)):
		v场景.set_voxel(vec3(i, j, -63), 1, vec3(1, 1, 1))
	#天花板
	for i, j in ti.ndrange((-64, 64), (-64, 64)):
		v场景.set_voxel(vec3(i, 63, j), 1, vec3(1, 1, 1))
f初始化()
v场景.finish()