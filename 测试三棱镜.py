import taichi as ti
from taichi.math import *
ti.init(arch=ti.vulkan)
c窗口宽度 = 1000
c窗口高度 = 1000
c窗口尺寸 = (c窗口宽度, c窗口高度)
c窗口半宽 = c窗口宽度 // 2
c窗口半高 = c窗口高度 // 2
c缩放 = 1 / 10
def lerp(a, b, t):
	return a + (b - a) * t
def f屏幕坐标(v):
	return vec2(v.x * c缩放 + 0.5, v.y * c缩放 + 0.5)
def f创建点场(a点):
	v数量 = len(a点)
	v场 = ti.Vector.field(2, dtype = float, shape = v数量)
	for i in range(v数量):
		v场[i] = f屏幕坐标(a点[i])
	return v场
def f创建线场(a点):
	v数量 = len(a点)
	v场 = ti.Vector.field(2, dtype = float, shape = v数量*2)
	#点位分布
	#0 1
	#2 3
	v点 = list(f屏幕坐标(x) for x in a点)
	v场[0] = v点[0]
	v场[1] = v点[1]
	v场[2] = v点[0]
	v场[3] = v点[2]
	v场[4] = v点[1]
	v场[5] = v点[3]
	v场[6] = v点[2]
	v场[7] = v点[3]
	return v场
@ti.data_oriented
class C四边形:
	def __init__(self, a, b, c, d):	#给定四边形四个点的坐标,初始化四边形uv计算器
		v原始点 = [a, b, c, d]
		self.o = a	#原点
		ob, oc = b-a, c-a
		self.m = mat2([[ob.x, oc.x], [ob.y, oc.y]])
		self.im = mat2([[oc.y, -oc.x], [-ob.y, ob.x]]) / (ob.x*oc.y - ob.y*oc.x)	#m的逆
		self.x0, self.y0 = self.im @ (d - a)
		self.uv = self.uv_x if self.x0 != 1 else (self.uv_y if self.y0 != 1 else self.uv_1)
		v转换点 = list(self.uv(x) for x in v原始点)
		v还原点 = list(self.xy(x) for x in v转换点)
		self.m点0 = f创建点场(v原始点)
		self.m点1 = f创建点场(v转换点)
		self.m点2 = f创建点场(v还原点)
		self.m线0 = f创建线场(v原始点)
		self.m线1 = f创建线场(v转换点)
		self.m线2 = f创建线场(v还原点)
	def uv_x(self, p):	#给定一点p=(x,y),计算p在四边形中的uv坐标.这是x0≠1的情况
		#解方程lerp(1,x0,v)*u=x和lerp(1,x0,u)*v=y.计算过程在草稿纸上
		x, y = self.im @ (p - self.o)
		a, b, c = self.x0-1, x*self.y0-x-(self.x0-1)*y+1, -y
		v = (-b + ti.sqrt(b*b - 4*a*c)) / (2*a)	#只取第一个解
		u = x / (1 + (self.x0-1)*v)
		return vec2(u, v)
	def uv_y(self, p):	#这是y0≠1的情况
		x, y = self.im @ (p - self.o)
		a, b, c = self.y0-1, y*self.x0-y-(self.y0-1)*x+1, -x
		u = (-b + ti.sqrt(b*b - 4*a*c)) / (2*a)	#只取第一个解
		v = y / (1 + (self.y0-1)*u)
		return vec2(u, v)
	def uv_1(self, p):	#这是x0=1且y0=1的情况
		x, y = self.im @ (p - self.o)
		return vec2(x, y)
	def xy(self, p):	#给定一点p=(u,v),计算p在四边形中的xy坐标
		return self.m @ vec2(lerp(1, self.x0, p.y)*p.x, lerp(1, self.y0, p.x)*p.y) + self.o
v坐标轴 = ti.Vector.field(2, dtype = float, shape = 4)
v坐标轴[0] = f屏幕坐标(vec2(-10, 0))
v坐标轴[1] = f屏幕坐标(vec2(10, 0))
v坐标轴[2] = f屏幕坐标(vec2(0, -10))
v坐标轴[3] = f屏幕坐标(vec2(0, 10))
v四边形 = C四边形(vec2(-1, 1), vec2(1, 1), vec2(-1, -1), vec2(1, -1))
v窗口 = ti.ui.Window("三棱镜", res = c窗口尺寸)
v画布 = v窗口.get_canvas()
while v窗口.running:
	v画布.lines(v坐标轴, 0.002, color = (0.5, 0.5, 0.5))
	v画布.lines(v四边形.m线0, 0.002, color = (1, 0.5, 0.5))
	v画布.lines(v四边形.m线1, 0.002, color = (0.5, 1, 0.5))
	v画布.lines(v四边形.m线2, 0.002, color = (0.5, 0.5, 1))
	v窗口.show()