from scene import Scene
import taichi as ti
from taichi.math import *
v场景 = Scene(voxel_edges = 0, exposure = 1)
v场景.set_floor(-8/64, (0.1, 0.1, 0.1))
v场景.set_directional_light((0, 1, 0), 0.1, (0.1, 0.1, 0.1))
N = 64	#大小
半N = N // 2
@ti.func
def lerp(a, b, t):
	return a + (b - a) * t
@ti.func
def rainbow(h: float, l: float):
	h = h * 6	#范围[0, 6],红橙黄绿青蓝紫
	r, g, b = 0.0, 0.0, 0.0
	if h < 1: r, g = 1, lerp(0, 0.5, h)	#红->橙
	elif h < 2:	r, g = 1, lerp(0.5, 1, h - 1)	#橙->黄
	elif h < 3:	r, g = lerp(1, 0, h - 2), 1	#黄->绿
	elif h < 4:	g, b = 1, lerp(0, 1, h - 3)	#绿->青
	elif h < 5:	g, b = lerp(1, 0, h - 4), 1	#青->蓝
	elif h < 6:	b, r = 1, lerp(0, 1, h - 5)	#蓝->紫
	else: b, r = lerp(1, 0, h - 6), 1	#紫->红
	return lerp(vec3(r, g, b), vec3(1, 1, 1), l)
@ti.data_oriented
class C四边形:	#一个不规则四边形
	def __init__(self, a, b, c, d):	#给定四边形四个点的坐标,初始化四边形uv计算器
		self.o = a	#原点
		ob, oc = b-a, c-a
		self.m = mat2([[ob.x, oc.x], [ob.y, oc.y]])
		self.im = mat2([[oc.y, -oc.x], [-ob.y, ob.x]]) / (ob.x*oc.y - ob.y*oc.x)	#m的逆
		self.x0, self.y0 = self.im @ (d - a)	#平行四边形会使得x0=1,y0=1,计算uv时需要分情况处理
		self.uv = self.uv_x if self.x0 != 1 else (self.uv_y if self.y0 != 1 else self.uv_1)
	@ti.func
	def uv_x(self, p):	#给定一点p=(x,y),计算p在四边形中的uv坐标.这是x0≠1的情况
		#解方程lerp(1,x0,v)*u=x和lerp(1,x0,u)*v=y.计算过程在草稿纸上
		x, y = self.im @ (p - self.o)
		a, b, c = self.x0-1, x*self.y0-x-(self.x0-1)*y+1, -y
		v = (-b + ti.sqrt(b*b - 4*a*c)) / (2*a)	#只取第一个解
		u = x / (1 + (self.x0-1)*v)
		return vec2(u, v)
	@ti.func
	def uv_y(self, p):	#这是y0≠1的情况
		x, y = self.im @ (p - self.o)
		a, b, c = self.y0-1, y*self.x0-y-(self.y0-1)*x+1, -x
		u = (-b + ti.sqrt(b*b - 4*a*c)) / (2*a)	#只取第一个解
		v = y / (1 + (self.y0-1)*u)
		return vec2(u, v)
	@ti.func
	def uv_1(self, p):	#这是x0=1且y0=1的情况
		x, y = self.im @ (p - self.o)
		return vec2(x, y)
	@ti.func
	def xy(self, p):	#给定一点p=(u,v),计算p在四边形中的xy坐标
		return self.m @ vec2(lerp(1, self.x0, p.y)*p.x, lerp(1, self.y0, p.x)*p.y) + self.o
v光线0 = C四边形(vec2(-64,18), vec2(-64,14), vec2(-16,2), vec2(-14,-3))	#提前计算好光线折射路径
v光线1 = C四边形(vec2(-16,2), vec2(-14,-3), vec2(20,10), vec2(12,-6))
v光线2 = C四边形(vec2(20,10), vec2(12,-6), vec2(63,48), vec2(63,0))
v亮度0, v亮度1, v亮度2, v亮度3 = 1, 1, 0.2, 0.1	#随光线分散开来逐渐变暗
@ti.func
def f生成光线(a四边形, a亮度0, a亮度1, x, y):
	u, v = a四边形.uv(vec2(x, y))
	if (0 <= u <= 1) and (0 <= v <= 1):
		c = rainbow(1-u, lerp(a亮度0, a亮度1, v))
		v场景.set_voxel(vec3(x, 1, y), 2, c)
		v场景.set_voxel(vec3(x, 0, y), 2, c)
		v场景.set_voxel(vec3(x, -1, y), 2, c)
		# v场景.set_voxel(vec3(x, 0, y), 2, vec3(u, v, 0)) 
@ti.kernel
def f初始化():
	#三角形
	for i, j in ti.ndrange(半N, N):
		if i < j // 2:	#三角形底边在z正方向
			v场景.set_voxel(vec3(i, 0, j - 半N), 1, vec3(0.5, 0.5, 0.5))
			v场景.set_voxel(vec3(-i, 0, j - 半N), 1, vec3(0.5, 0.5, 0.5))
	#入射光,从左边射入
	for i, j in ti.ndrange((-N, N), (-N, N)):
		f生成光线(v光线0, v亮度0, v亮度1, i, j)
	#折射光
	for i, j in ti.ndrange((-N, N), (-N, N)):
		f生成光线(v光线1, v亮度1, v亮度2, i, j)
	#出射光
	for i, j in ti.ndrange((-N, N), (-N, N)):
		f生成光线(v光线2, v亮度2, v亮度3, i, j)
f初始化()
v场景.finish()