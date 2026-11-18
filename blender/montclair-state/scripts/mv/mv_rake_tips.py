# Session mv (Oct 29 2026): S-corner "rake-tip points" at the CCOM west entrance gable.
# Probe (mv_probe2) showed the dark spikes are LiDAR-roof eave triangles (faces 19169/19740 etc.) whose
# outer verts sit at u 3.76 / w 23.14 -- past the mu eave-return box front (w 23.005) and 0.57 m into the
# pavilion side (u 3.19). Same eave verts at the N side (u 10.67/11.36, w 23.14) poke 0.14 m past the N return front -> same fix. Pull those verts back inside the return box so the triangles are hidden.
import bpy, sys
from mathutils import Vector
n=Vector((-0.972,0.232,0)).normalized(); t=Vector((0.232,0.972,0)).normalized()
DRY='--dry' in sys.argv
o=bpy.data.objects['School of Communication and Media roof (LiDAR)']
me=o.data; mw=o.matrix_world; mi=mw.inverted()
cand=[]
for v in me.vertices:
    g=mw@v.co; u=g.dot(t); w=g.dot(n)
    if 146.3<g.z<147.2 and w>22.93 and 2.5<u<4.2: cand.append(v.index); print('S cand',v.index,round(u,3),round(w,3),round(g.z,3))
    if 146.3<g.z<147.2 and w>22.93 and 10.3<u<11.6: print('N cand (report only; strip u 9.98-11.79 shares these verts, left)',v.index,round(u,3),round(w,3),round(g.z,3))
cs=set(cand)
for p in me.polygons:
    if cs & set(p.vertices):
        vs=[mw@me.vertices[i].co for i in p.vertices]
        print(' face',p.index,'mat',p.material_index,'u',[round(x.dot(t),2) for x in vs],'w',[round(x.dot(n),2) for x in vs],'z',[round(x.z,2) for x in vs])
if not DRY:
    for i in cand:
        g=mw@me.vertices[i].co; u=g.dot(t); w=g.dot(n)
        nu=min(u,3.05) if u<6 else max(u,10.45); nw=22.80
        h=t*nu+n*nw; g2=Vector((h.x,h.y,min(max(g.z,146.60),146.95)))
        me.vertices[i].co=mi@g2
        print('moved',i,'->u',round(nu,3),'w',nw,'z',round(g2.z,3))
    me.update()
    o['mv_note']='mv Oct 29 2026: %d S-corner eave verts pulled inside the mu return box (rake-tip spikes); UNVERIFIED detail'%len(cand)
    print('COUNT',len(bpy.data.objects))
    bpy.ops.wm.save_mainfile(); print('SAVED')
