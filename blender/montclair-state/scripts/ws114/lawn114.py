# ws114: lift lawn (fan fill + WS110 ground patch base verts) to meet the brick link / WS111 E walk edges (no exposed 15-20 cm brick side)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=lambda p: next(o for o in bpy.data.objects if o.name.startswith(p))
tops=[];planes=[]
for p in ('WS112_CollegeAve_S_E_walk_N_brick','WS111_CollegeAve_S_E_walk_gap'):
    o=O(p); me=o.data; mw=o.matrix_world
    for f in me.polygons:
        if f.normal.z<0.7: continue
        vs=[mw@me.vertices[i].co for i in f.vertices]
        tops.append([Vector((v.x,v.y,0)) for v in vs]); planes.append((vs[0],(mw.to_3x3()@f.normal).normalized()))
verts=[];polys=[]
for t in tops:
    b=len(verts); verts+=t; polys.append(list(range(b,b+len(t))))
bvh=BVHTree.FromPolygons(verts,polys)
def zat(i,x,y):
    p0,n=planes[i]; return p0.z-(n.x*(x-p0.x)+n.y*(y-p0.y))/n.z
tot=0
for p in ('WS113_terrain_fan_fill','WS110_ground_patch'):
    o=O(p); me=o.data; mw=o.matrix_world; inv=mw.inverted(); n=0; mx=0
    for v in me.vertices:
        w=mw@v.co; loc,nor,idx,d=bvh.find_nearest(Vector((w.x,w.y,0)),1.3)
        if loc is None or d<0.02: continue
        ze=zat(idx,loc.x,loc.y)
        tgt=ze-0.03-0.12*d
        if w.z<tgt:
            mx=max(mx,tgt-w.z); w.z=tgt; v.co=inv@w; n+=1
    me.update(); print('L114',o.name[:30],'lifted',n,'max %.3f'%mx); tot+=n
bpy.ops.wm.save_mainfile(); print('L114 SAVED main',tot)
