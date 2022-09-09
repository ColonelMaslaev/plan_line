# исходный файл - plan.xml, конвертированная в трассу полилиния из робура
# итоговый файл - result.xml, уложенная ось

import math

# дирекционный угол линии в градусах
def a_angle(x1, y1, x2, y2):
	dx = x1 - x2
	dy = y1 - y2
	if dy == 0:
		if dx >= 0:
			a = 270.0
		else:
			a = 90.0
	else:
		rb = abs(math.degrees(math.atan(dx / dy)))
		if dx > 0:
			if dy > 0:
				a = rb + 180
			else:
				a = 360 - rb
		elif dx < 0:
			if dy > 0:
				a = 180 - rb
			else:
				a = rb
		else:
			if dy > 0:
				a = 180.0
			else:
				a = 0.0
	return a

# радиус окружности по трем точкам (используется, но не нужен)
def radius(x1, y1, x2, y2, x3, y3):
	a1 = a_angle(x1, y1, x2, y2)
	a2 = a_angle(x2, y2, x3, y3)
	px1 = (x1 + x2) / 2
	py1 = (y1 + y2) / 2
	px2 = (x2 + x3) / 2
	py2 = (y2 + y3) / 2
	if (a1 == 0) or (a1 == 180):
		k1 = 0
		b1 = py1
	elif (a1 == 90) or (a1 == 270):
		k1 = 0
		b1 = px1
	else:
		k1 = math.tan(math.radians(180 - a1))
		b1 = py1 - k1 * px1
	if (a2 == 0) or (a2 == 180):
		k2 = 0
		b2 = py2
	elif (a2 == 90) or (a2 == 270):
		k2 = 0
		b2 = px2
	else:
		k2 = math.tan(math.radians(180 - a2))
		b2 = py2 - k2 * px2	
	if k1 != k2:
		if (k1 != 0) and (k2 != 0):
			rx = (b2 - b1) / (k1 - k2)
			ry = k1 * rx + b1
		else:
			if (a1 == 0) or (a1 == 180):
				ry = py1
				rx = (ry - b2) / k2
			elif (a1 == 90) or (a1 == 270):
				rx = px1
				ry = k2 * rx + b2
			elif (a2 == 0) or (a2 == 180):
				ry = py2
				rx = (ry - b1) / k1
			elif (a2 == 90) or (a2 == 270):
				rx = px2
				ry = k1 * rx + b1
		r = length(x2, y2, rx, ry)
		# радиус с минусом - поворот вправо, без минуса - влево
		if (a2 > a1) and ((a2 - a1) < 180):
			r = -r
		elif (a1 > a2) and ((a1 - a2) > 180):
			r = -r
	else:
		r = 0
	return r

# запись в файл
def to_file(xv, yv, rv):
	lines = []
	lines.append('<?xml version="1.0" encoding="utf-8"?>')
	lines.append('<Stg>')
	lines.append('  <Body>')
	lines.append('    <PlanLine>')
	lines.append('      <PlanVertexes aType="0">')
	for i in range(0, len(xv)):
		lines.append('        <Vertex>')
		if i == 0:
			lines.append('          <Name>НТ</Name>')
		elif i == len(xv) - 1:
			lines.append('          <Name>КТ</Name>')
		else:
			lines.append('          <Name>' + str(i) + '</Name>')
		lines.append('          <CoordX>' + str(xv[i]) + '</CoordX>')
		lines.append('          <CoordY>' + str(yv[i]) + '</CoordY>')
		lines.append('          <Station>0</Station>')
		lines.append('          <Beta>0</Beta>')
		lines.append('          <MinLineLength>0</MinLineLength>')
		lines.append('          <LastLength>0</LastLength>')
		if rv[i] != 0:
			lines.append('          <Items aType="0">')
			lines.append('            <Items>')
			lines.append('              <Length>0</Length>')
			lines.append('              <Radius>' + str(rv[i]) + '</Radius>')
			lines.append('              <Quota>100</Quota>')
			lines.append('            </Items>')
			lines.append('          </Items>')
		lines.append('          <ID>' + str(i + 1) + '</ID>')
		lines.append('        </Vertex>')
	lines.append('      </PlanVertexes>')
	lines.append('      <MultiRadiusExtendedPCalculation>false</MultiRadiusExtendedPCalculation>')
	lines.append('      <AutomaticNames>true</AutomaticNames>')
	lines.append('    </PlanLine>')
	lines.append('  </Body>')
	lines.append('</Stg>')
	with open('result.xml', 'w', encoding='utf-8') as f:
		for line in lines:
			f.write(line)
			f.write('\n')

# расстояние от точки xyi до прямой xyb xye
def line_deviation(xb, yb, xi, yi, xe, ye):
	a = a_angle(xb, yb, xe, ye)
	b = a_angle(xb, yb, xi, yi)
	g = math.radians(abs(a - b))
	d = (length(xb, yb, xi, yi)) * (math.sin(g))
	return d

# расстояние от точки xyi до дуги между xyb и xye с вершиной в точке xyv
def curve_deviation(xb, yb, xe, ye, xv, yv, xi, yi):
	# длины плеч
	v1 = length(xb, yb, xv, yv)
	v2 = length(xe, ye, xv, yv)
	# выбор меньшего плеча и укорачивание большего с запоминанием измененных координат
	if v1 != v2:
		t = r_tan(xb, yb, xv, yv, xe, ye)
		r = t[0]
		xp = t[1]
		yp = t[2]
		if xp == xb:
			xo = xe
			yo = ye
			xe = xp
			ye = yp
		else:
			xo = xb
			yo = yb
			xb = xp
			yb = yp
	# подсчет координат центра дуги
	xh = (xb + xe) / 2
	yh = (yb + ye) / 2
	a = a_angle(xv, yv, xh, yh)
	l = length(xh, yh, xp, yp)
	v = length(xp, yp, xv, yv)
	dv = math.sqrt(abs(v ** 2 - l ** 2))
	h = math.sqrt(abs(r ** 2 - l ** 2))
	dr = dv + h
	xr = xv + dr * math.sin(math.radians(a))
	yr = yv + dr * math.cos(math.radians(a))
	# расстояние от точки xyi до дуги
	if v1 == v2:
		cd = abs(length(xr, yr, xi, yi) - r)
	# расстояние от точки xyi до прямой (при неравенстве плеч) перед или за дугой
	else:
		tan = line_angle(xo, yo, xp, yp)
		if yo == yi:
			tanp = [1, 0, xi]
		else:
			tanp = [0, (-1 / tan[1]), (yi - (-1 / tan[1]) * xi)]
		if tan[0] == 1:
			xn = tan[2]
			yn = tanp[1] * xn + tanp[2]
		elif tanp[0] == 1:
			xn = tanp[2]
			yn = tan[1] * xn + tan[2]
		else:
			xn = (tanp[2] - tan[2]) / (tan[1] - tanp[1])
			yn = tan[1] * xn + tan[2]
		if (xn <= max(xo, xp)) and (xn >= min(xo, xp)):
			cd = length(xi, yi, xn, yn)
		else:
			cd = abs(length(xr, yr, xi, yi) - r)
	return cd

# направление трассы в точке (не используется)
def direction(r):
	if r > 0:
		return 1  # влево
	elif r < 0:
		return 2  # вправо
	else:
		return 0  # прямо

# угловые коэффициенты прямой [1, 0, x] в случае вертикальной прямой, [0, k, b] в любом другом
def line_angle(x1, y1, x2, y2):
	a = a_angle(x1, y1, x2, y2)
	if (a == 180) or (a == 0):
		return [1, 0, x1]
	else:
		k = round(math.tan(math.radians(90 - a)), 10)
		b = round(y1 - k * x1, 10)
		return [0, k, b]

# длина отрезка между точками сука это пиздец поставить плюс вместо минуса и два часа искать наебку
def length(x1, y1, x2, y2):
	l = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
	return l

# уравнение прямой, касательной к точке (биссектриса между двумя прямыми) - [1, 0, x] в случае вертикальной прямой, [0, k, b] в любом другом
def tangent(x1, y1, x2, y2, x3, y3):
	a1 = a_angle(x1, y1, x2, y2)
	a2 = a_angle(x2, y2, x3, y3)
	a = (a1 + a2) / 2
	if (a == 180) or (a == 0):
		return [1, 0, x2]
	else:
		k = round(math.tan(math.radians(90 - a)), 10)
		b = round(y2 - k * x2, 10)
	return [0, k, b]

# расчет радиуса исходя из меньшего плеча (возвращает также пересчитанные по меньшему плечу координаты в сторону большего для функции curve_deviation)
def r_tan(xb, yb, xv, yv, xe, ye):
	v1 = length(xb, yb, xv, yv)
	v2 = length(xe, ye, xv, yv)
	if v1 < v2:
		xp = xe - ((xe - xv) * (v2 - v1)) / v2
		yp = ye - ((ye - yv) * (v2 - v1)) / v2
		l = length(xp, yp, xb, yb) / 2
		v = v1
	else:
		xp = xb - ((xb - xv) * (v1 - v2)) / v1
		yp = yb - ((yb - yv) * (v1 - v2)) / v1
		l = length(xp, yp, xe, ye) / 2
		v = v2
	r = (v * l) / (math.sqrt((v ** 2) - (l ** 2)))
	return r, xp, yp

# расчет координат вершины дуги по спискам кординат вершин и индексам первой и второй точек
def v_tan(x, y, ib, ie):
	# касательные прямые в первой и второй точках дуги
	if ib == 0:
		tan1 = line_angle(x[ib], y[ib], x[ib + 1], y[ib + 1])
	else:
		tan1 = tangent(x[ib - 1], y[ib - 1], x[ib], y[ib], x[ib + 1], y[ib + 1])
	if ie == (len(x) - 1):
		tan2 = line_angle(x[ie], y[ie], x[ie - 1], y[ie - 1])
	else:
		tan2 = tangent(x[ie - 1], y[ie - 1], x[ie], y[ie], x[ie + 1], y[ie + 1])
	# координаты вершины дуги
	if tan1[0] == 1:
		xv = tan1[2]
		yv = tan2[1] * xv + tan2[2]
	elif tan2[0] == 1:
		xv = tan2[2]
		yv = tan1[1] * xv + tan1[2]
	else:
		xv = (tan2[2] - tan1[2]) / (tan1[1] - tan2[1])
		yv = tan1[1] * xv + tan1[2]
	return xv, yv

# чтение файла
with open('plan.xml') as f:
	lines = f.readlines()
# начало списка координат
ns = -1
for line in lines:
	ns += 1
	if '<PlanVertexes' in line:
		break
# конец списка координат
ne = -1
for line in lines:
	ne += 1
	if '</PlanVertexes' in line:
		break
# извлечение координат исходных точек
x = []
y = []
for i in range(ns + 1, ne - 1, 10):
	xs = lines[i + 2][18:].index('<')
	ys = lines[i + 3][18:].index('<')
	x.append(float(lines[i + 2][18:xs + 18]))
	y.append(float(lines[i + 3][18:ys + 18]))
# список радиусов кривизны (не используется)
# r = [0]
# for i in range(1, len(x) - 1):
# 	r.append(radius(x[i - 1], y[i - 1], x[i], y[i], x[i + 1], y[i + 1]))
# r.append(0)
# списки координат вершин оси и радиусов
xv = [x[0]]
yv = [y[0]]
rv = [0]
li = [0]  # список индексов вершин
ib = 0  # индекс первой точки рассматриваемого участка
ie = 0  # индекс последней точки рассматриваемого участка
lt = 0.15  # допустимое отклонение на прямой
ct = 0.25  # допустимое отклонение на дуге
while ib < (len(x) - 1):
	ie = ib
	il = ib  # индекс последней встреченной точки, для которого прямая ib - il удовлетворяет допускам
	ic = ib  # индекс последней встреченной точки, для которого дуга ib - ic удовлетворяет допускам
	while (ie < (len(x) - 1)) and ((ie - il) < 15) and ((ie - ic) < 15):  # если n последних точек не удовлетворяют допускам ни по прямой, ни по дуге, цикл останавливается
		ie += 1
		ld = 0  # отклонение от прямой
		cd = 0  # отклонение от дуги
		# координаты вершины дуги для рассматриваемого участка
		vv = v_tan(x, y, ib, ie)
		xvi = vv[0]
		yvi = vv[1]
		# длина плеч дуги (расстояний от вершины дуги до начала и конца участка)
		vb = length(x[ib], y[ib], xvi, yvi)
		ve = length(x[ie], y[ie], xvi, yvi)
		l = length(x[ib], y[ib], x[ie], y[ie])
		# поиск максимального отклонения от прямой и от дуги на участке
		for i in range(ib + 1, ie):
			if line_deviation(x[ib], y[ib], x[i], y[i], x[ie], y[ie]) > ld:
				ld = line_deviation(x[ib], y[ib], x[i], y[i], x[ie], y[ie])
			if curve_deviation(x[ib], y[ib], x[ie], y[ie], xvi, yvi, x[i], y[i]) > cd:
				cd = curve_deviation(x[ib], y[ib], x[ie], y[ie], xvi, yvi, x[i], y[i])
		# условия для прямой (отклонение в допуске, длина более 50 метров или до конца трассы)
		# также срабатывает если участок предельно мал (между соседними точками) на случай, если между ними не вписать радиус, а дальше срабатывания не будет (при зигзагообразной линии)
		if ((ld < lt) and ((l > 50) or (ie == (len (x) - 1)))) or ((ie - ib) == 1):
			il = ie
		# условия для дуги (отклонение в допуске, разница плеч не более n * меньшее, плечи не больше длины участка)
		if (cd < ct) and (abs(vb - ve) < min(vb, ve) * 0.5) and (vb < l) and (ve < l):
			ic = ie
	# запись прямой (вершина на конце участка)
	if (il > ic) or ((il == ic) and ((il - ib) > 1)):
		xv.append(x[il])
		yv.append(y[il])
		rv.append(0)
		li.append(il)
		ib = il
	# запись дуги (вершина дуги, вершина на конце участка)
	else:
		vv = v_tan(x, y, ib, ic)
		xv.append(vv[0])
		yv.append(vv[1])
		rv.append(r_tan(x[ib], y[ib], xv[-1], yv[-1], x[ic], y[ic])[0])
		li.append((ib + ic) / 2)
		xv.append(x[ic])
		yv.append(y[ic])
		rv.append(0)
		li.append(ic)
		ib = ic
# удаление вершин без изгиба между дугами
i = 0
while i < (len(xv) - 2):
	i += 1
	if (rv[i - 1] != 0) and (rv[i] == 0) and (rv[i + 1] != 0):
		del xv[i]
		del yv[i]
		del rv[i]
		del li[i]
		i -= 1
# спрямление зигзагов	
i = 0
while i < (len(xv) - 1):
	ib = i
	while ((li[i + 1] - li[i]) == 1) and (rv[i] == 0) and (rv[i + 1] == 0):
		i += 1
	ie = i
	if (ie - ib) > 1:
		ld = 0
		for j in range(ib + 1, ie):
			if line_deviation(x[ib], y[ib], x[j], y[j], x[ie], y[ie]) > ld:
				ld = line_deviation(x[ib], y[ib], x[j], y[j], x[ie], y[ie])
		if ld < lt:
			n = ie - ib - 1
			for j in range(n):
				del xv[ib + 1]
				del yv[ib + 1]
				del rv[ib + 1]
				del li[ib + 1]
				i -= 1
			i -= 1
	i += 1
to_file(xv, yv, rv)