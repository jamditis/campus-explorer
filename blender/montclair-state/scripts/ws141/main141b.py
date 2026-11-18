# ws141b: (1) ortho-drape ground under the BK NE-corner tree -> lawn (ortho: deep tree shadow; LiDAR: no ground returns = dense canopy, no paving)
# (2) lawn feathered flush to the new pad edges (was 5-15 cm below -> visible slab edge)
import bpy, bmesh, os, numpy as np
from mathutils import Vector, kdtree
OB=bpy.data.objects
LAWN=bpy.data.materials['COLE_lawn_post2020_bs']
REG=(-88,-74.75,-216.6,-202.5)
def isortho(m):
    if m is None: return False
    n=m.name.lower()
    return ('ortho' in n) and not any(k in n for k in ('asphalt','walk','curb','paint','road','concrete','brick','roof'))
pad=[o for o in OB if o.name.startswith('WS141_BK_NE_concrete_pad')][0]
pm=pad.data; pmw=pad.matrix_world
top=[pmw@v.co for v in pm.vertices]
# boundary verts of the top surface (highest per xy)
bmp=bmesh.new(); bmp.from_mesh(pm)
B=[pmw@e.verts[0].co for e in bmp.edges if any(f.normal.z>0.5 for f in e.link_faces) and any(abs(f.normal.z)<0.5 for f in e.link_faces)]
B+=[pmw@e.verts[1].co for e in bmp.edges if any(f.normal.z>0.5 for f in e.link_faces) and any(abs(f.normal.z)<0.5 for f in e.link_faces)]
bmp.free()
kd=kdtree.KDTree(len(B))
for i,p in enumerate(B): kd.insert(Vector((p.x,p.y,0)),i)
kd.balance()
xs=[p.x for p in B]; ys=[p.y for p in B]
bx0,bx1,by0,by1=min(xs)-1.6,max(xs)+0.1,min(ys)-1.6,max(ys)+1.6
# inside test via ray down onto the pad
def inside(x,y):
    o=pmw.inverted()@Vector((x,y,500)); h=pad.ray_cast(o,Vector((0,0,-1)))
    return h[0]
tex={}; gr={}
for o in OB:
    if o.type!='MESH' or 'tree' in o.name.lower() or o.name.startswith(('WS136a_','WS134_Balance','WS135','WS141_','WS139_walk')): continue
    me=o.data; mw=o.matrix_world
    bb=[mw@Vector(c) for c in o.bound_box]
    if max(v.x for v in bb)<-88 or min(v.x for v in bb)>-66 or max(v.y for v in bb)<-222 or min(v.y for v in bb)>-200: continue
    mats=list(me.materials)
    if any(isortho(m) for m in mats):
        li=None
        for i,m in enumerate(mats):
            if m==LAWN: li=i
        hit=[]
        for p in me.polygons:
            m=mats[p.material_index] if p.material_index<len(mats) else None
            if not isortho(m): continue
            c=mw@p.center
            if REG[0]<c.x<REG[1] and REG[2]<c.y<REG[3]: hit.append(p)
        if hit:
            if li is None: me.materials.append(LAWN); li=len(me.materials)-1
            for p in hit: p.material_index=li
            tex[o.name[:40]]=len(hit)
    if not o.name.startswith(('Terrain','WS114','WS134_ground','WS133b_ground','WS110_ground')): continue
    mi=mw.inverted(); n=0
    for v in me.vertices:
        p=mw@v.co
        if not (bx0<p.x<bx1 and by0<p.y<by1): continue
        co,i,d=kd.find(Vector((p.x,p.y,0)))
        if d>1.5: continue
        if inside(p.x,p.y): continue
        zt=B[i].z-0.025
        w=1.0 if d<0.6 else (1.5-d)/0.9
        if abs(p.z-zt)>0.6: continue
        p.z=p.z+(zt-p.z)*w; v.co=mi@p; n+=1
    if n: me.update(); gr[o.name[:40]]=n
    else: me.update()
print('RETEX',tex); print('FEATHER',gr)
bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUT'],copy=True); print('SAVED')
