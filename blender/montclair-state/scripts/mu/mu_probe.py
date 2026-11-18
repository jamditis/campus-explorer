# Session mu: probe open boundary edges created by mt eave trim at the gable sides
import bpy, bmesh
from mathutils import Vector
n=Vector((-0.972,0.232,0)).normalized(); t=Vector((0.232,0.972,0)).normalized()
U0,U1=3.197,10.397
skip=('CCOM entrance','CCOM tower','CCOM atrium')
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(v.z for v in bb)<145.5 or min(v.z for v in bb)>149.5: continue
    if max(v.dot(n) for v in bb)<20.5 or min(v.dot(n) for v in bb)>24.5: continue
    if min(v.dot(t) for v in bb)>U1+1.5 or max(v.dot(t) for v in bb)<U0-1.5: continue
    mw=o.matrix_world
    bm=bmesh.new(); bm.from_mesh(o.data)
    side={-1:[],1:[]}
    for e in bm.edges:
        if not e.is_boundary: continue
        a=mw@e.verts[0].co; b=mw@e.verts[1].co
        for s,U in ((-1,U0),(1,U1)):
            if all(abs(p.dot(t)-U)<0.12 for p in (a,b)) and all(20.8<p.dot(n)<24.2 and 145.5<p.z<149 for p in (a,b)):
                side[s].append((a,b))
    if side[-1] or side[1]:
        print('OBJ',repr(o.name),'mats',[m.name if m else None for m in o.data.materials],'users',o.data.users)
        for s in side:
            pts=[p for e in side[s] for p in e]
            if pts: print('  side',s,'nedges',len(side[s]),'u',round(min(p.dot(t) for p in pts),3),round(max(p.dot(t) for p in pts),3),'w',round(min(p.dot(n) for p in pts),3),round(max(p.dot(n) for p in pts),3),'z',round(min(p.z for p in pts),3),round(max(p.z for p in pts),3))
    bm.free()
# gable objects bounds
for o in bpy.data.collections['MS_CCOM_entrance_gable_20261029mt'].objects:
    vs=[o.matrix_world@v.co for v in o.data.vertices]
    print('G',o.name,'w',round(min(v.dot(n) for v in vs),3),round(max(v.dot(n) for v in vs),3),'u',round(min(v.dot(t) for v in vs),3),round(max(v.dot(t) for v in vs),3),'z',round(min(v.z for v in vs),3),round(max(v.z for v in vs),3))
print('COUNT',len(bpy.data.objects))
