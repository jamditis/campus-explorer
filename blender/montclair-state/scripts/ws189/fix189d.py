# ws189d: smooth gooseneck (quarter-circle bend, R = base-to-bar offset 1.9 m, 17 pts) replacing fix189b's kinked polyline.
import bpy, math
_o=bpy.data.objects.get('WS189_goalpost_gooseneck_LiDAR2023_ortho2020')
_bar=bpy.data.objects.get('WS189_goalpost_crossbar_10ft_LiDAR2023')
_sp=_o.data.splines[0]; _pts=[p.co for p in _sp.points]
CXd=_pts[0][0]; YBd=_pts[0][1]; GBd=_pts[0][2]; _bp=_bar.data.splines[0].points[0].co; YCd=_bp[1]; ZBd=_bp[2]
R=YCd-YBd; z0=ZBd-R
new=[(CXd,YBd,GBd)]+[(CXd,YBd+R*(1-math.cos(math.radians(90*i/16))),z0+R*math.sin(math.radians(90*i/16))) for i in range(17)]
_o.data.splines.clear(); s=_o.data.splines.new('POLY'); s.points.add(len(new)-1)
for i,q in enumerate(new): s.points[i].co=(q[0],q[1],q[2],1)
print('FIX189D gooseneck pts',len(new),'R',round(R,3),'z0',round(z0,3),'end',tuple(round(v,3) for v in new[-1]),flush=True)
