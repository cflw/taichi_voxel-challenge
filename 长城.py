from scene import Scene
import taichi as ti
from taichi.math import *
v场景 = Scene(voxel_edges = 0, exposure = 1)
v场景.set_floor(-1, (0.1, 0.1, 0.1))
v场景.set_background_color((0.5, 0.5, 0.9))
v场景.set_directional_light((0.5, 2, 1), 0.1, (1, 1, 1))
H0, H1, H2, A, w, Z = -44, -22, -4, 4, 1/10, 4	#地面中心高度,敌楼一楼,二楼,波的振幅,周期,砖的高度
@ti.func
def random3():
	return vec3(ti.random(), ti.random(), ti.random())
@ti.func
def f火把(p, d):
	for i in range(4):
		v场景.set_voxel(p, 1, vec3(0.5, 0.3, 0.1) + random3()*0.05)
		p += d
	v场景.set_voxel(p, 2, vec3(1, 0.6, 0.2))
@ti.kernel
def f初始化():
	for x, z in ti.ndrange((-64, 64), (-64, 64)):	#地面
		h = ti.sin(x * w) * A * (128 - ti.abs(z)) / 128 * ti.cos(z / 27.0) - ti.abs(z)/4 + H0
		for y in range(-64, h):
			v场景.set_voxel(vec3(x, y, z), 1, vec3(0.2, 0.4, 0) + random3()*0.1)
	for x in range(-64, 64):	#边墙
		h = ti.sin(x * w) * A + H0	#地面高度
		for y, z in ti.ndrange((h-10, h+20), (-8, 9)):	#中间过道,宽16格
			v场景.set_voxel(vec3(x, y, z), 1, vec3(0.8, 0.6, 0.2) + random3()*0.1)
		for y, z in ti.ndrange((h-10, h+30), (9, 11)):	#两边,垛墙厚2格
			v场景.set_voxel(vec3(x, y, z), 1, vec3(0.8, 0.6, 0.2) + random3()*0.1)
			v场景.set_voxel(vec3(x, y, -z), 1, vec3(0.8, 0.6, 0.2) + random3()*0.1)
	for i in range(8):	#挖洞,间隔16格
		x0 = i * 16
		h0 = ti.sin(x0 * w) * A + H0
		h5 = ti.sin((x0+5) * w) * A + H0
		h10 = ti.sin((x0+10) * w) * A + H0
		min0 = ti.min(h0, h5)
		for x, y, z in ti.ndrange((0, 6), (0, 20), (9, 11)):	#垛口宽6格
			v场景.set_voxel(vec3(x0 + x, y+min0+26, z), 0, vec3(0, 0, 0))	#垛墙的垛口
		for x, y, z in ti.ndrange((0, 2), (0, 2), (9, 11)):
			x1 = x0 + x + 10
			v场景.set_voxel(vec3(x1, y+h10+22, z), 0, vec3(0, 0, 0))	#垛墙的射口
			v场景.set_voxel(vec3(x1, y+h10+22, -z), 0, vec3(0, 0, 0))	#宇墙的射口
	for x, y, z in ti.ndrange((-20, 21), (H0-10, H2), (-20, 21)):	#敌楼主体
		v场景.set_voxel(vec3(x, y, z), 1, vec3(0.8, 0.6, 0.2) + random3()*0.1)
	for x, y, z in ti.ndrange((-20, 21), (H2, H2+10), (-20, 21)):	#敌楼垛墙
		if ti.abs(x) >= 19 or ti.abs(z) >= 19:
			v场景.set_voxel(vec3(x, y, z), 1, vec3(0.8, 0.6, 0.2) + random3()*0.1)
	for j, x, h in ti.ndrange((0, 4), (-3, 4), (0, 10)):	#挖敌楼垛墙
		for i in range(-1, 2):	#挖3个洞
			x1 = i * 12 + x
			v场景.set_voxel(vec3(x1, H2+h+4, 20-j), 0, vec3(0, 0, 0))
			v场景.set_voxel(vec3(x1, H2+h+4, -20+j), 0, vec3(0, 0, 0))
			v场景.set_voxel(vec3(20-j, H2+h+4, x1), 0, vec3(0, 0, 0))
			v场景.set_voxel(vec3(-20+j, H2+h+4, x1), 0, vec3(0, 0, 0))
			v场景.set_voxel(vec3(x1, H1+h+4, 20-j), 0, vec3(0, 0, 0))	#敌楼箭窗
			v场景.set_voxel(vec3(x1, H1+h+4, -20+j), 0, vec3(0, 0, 0))	#敌楼箭窗
		v场景.set_voxel(vec3(20-j, H1+h, x), 0, vec3(0, 0, 0))	#门
		v场景.set_voxel(vec3(-20+j, H1+h, x), 0, vec3(0, 0, 0))	#门
	for x, y, z in ti.ndrange((-18, 19), (H1, H2-2), (-18, 19)):	#敌楼内部
		v场景.set_voxel(vec3(x, y, z), 0, vec3(0, 0, 0))
	for x, y, z in ti.ndrange((-3, 4), (H2-2, H2+1), (-3, 4)):	#敌楼天花板的洞,宽6格
		v场景.set_voxel(vec3(x, y, z), 0, vec3(0, 0, 0))
	for y in range(H1, H2):	#梯子
		if y % 6 == 0:
			for x in range(-3, 4):
				v场景.set_voxel(vec3(x, y, 3), 1, vec3(0.5, 0.3, 0.1) + random3()*0.05)
		else:
			v场景.set_voxel(vec3(-3, y, 3), 1, vec3(0.5, 0.3, 0.1) + random3()*0.05)
			v场景.set_voxel(vec3(3, y, 3), 1, vec3(0.5, 0.3, 0.1) + random3()*0.05)
	for i in range(2):	#敌楼两侧台阶
		s = -1 if i else 1
		x = 20 * s
		y0 = int(ti.sin(x * w) * A + H0 + 20)
		while y0 != H1:
			for y in range(y0, H1):
				for z in range(-3, 4):
					v场景.set_voxel(vec3(x, y, z), 0, vec3(0, 0, 0))
			y0 += 1 if y0 < H1 else -1
			x -= s
	for x, y, z in ti.ndrange((-8, 9), (H2, H2+17), (-8, 9)):	#楼橹墙壁
		if (ti.abs(x) >= 7 or ti.abs(z) >= 7) and not (y <= H2+8 and ti.abs(z) <= 3):	#墙壁&门
			v场景.set_voxel(vec3(x, y, z), 1, vec3(0.8, 0.6, 0.2) + random3()*0.1)
	for x, y, z in ti.ndrange((-9, 10), (H2+16, H2+26), (-10, 11)):	#楼橹屋檐
		if H2+26-ti.abs(z) >= y:
			v场景.set_voxel(vec3(x, y, z), 1, vec3(0.2, 0.25, 0.15) + random3()*0.05)
	for i in range(2):	#火把
		x0 = (i-0.5)*12
		f火把(vec3(x0, H1+4, -18), vec3(0, 1, 0.4))	#一楼火把
		f火把(vec3(x0, H1+4, 18), vec3(0, 1, -0.4))
		f火把(vec3(-18, H1+4, x0), vec3(0.4, 1, 0))
		f火把(vec3(18, H1+4, x0), vec3(-0.4, 1, 0))
		x1 = (i-0.5)*10
		f火把(vec3(-6, H2+4, x1), vec3(0.4, 1, 0))	#二楼火把
		f火把(vec3(6, H2+4, x1), vec3(-0.4, 1, 0))
f初始化()
v场景.finish()