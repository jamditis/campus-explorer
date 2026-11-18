# Session mv: N analogue of the S rake-tip spike -- LiDAR roof eave strip at w 23.14 (u 9.98-11.79) pokes past the
# N eave-return box front (w 23.005) and in front of the gable face (u<10.397). Pull verts inside the return box.
import bpy, sys
from mathutils import Vector
n=Vector((-0.972,0.232,0)).normalized(); t=Vector((0.232,0.972,0)).normalized()
DRY='--dry' in sys.argv; UMAX=float([a for a in sys.argv if a.startswith('UMAX=')][0][5:]) if any(a.startswith('UMAX=') for a in sys.argv) else 11.5
o=bpy.data.objects['School of Communication and Media roof (LiDAR)']; me=o.data; mw=o.matrix_world; mi=mw.inverted()
cand=[v.index for v in me.vertices if 146.3<(mw@v.co).z<147.2 and (mw@v.co).dot(n)>22.93 and 9.8<(mw@v.co).dot(t)<UMAX]
cs=set(cand)
for p in me.polygons:
    if cs & set(p.vertices):
        vs=[mw@me.vertices[i].co for i in p.vertices]
        print(' face',p.index,'u',[round(x.dot(t),2) for x in vs],'w',[round(x.dot(n),2) for x in vs],'z',[round(x.z,2) for x in vs])
for i in cand:
    g=mw@me.vertices[i].co; u=g.dot(t); nu=max(u,10.45); h=t*nu+n*22.80
    print('cand',i,round(u,3),round(g.dot(n),3),round(g.z,3),'->',round(nu,3),22.80)
    if not DRY: me.vertices[i].co=mi@Vector((h.x,h.y,g.z))
if not DRY:
    me.update(); o['mv_note_N']='mv Oct 29 2026: %d N-corner eave verts pulled inside the mu N return box; UNVERIFIED'%len(cand)
    print('COUNT',len(bpy.data.objects)); bpy.ops.wm.save_mainfile(); print('SAVED')
