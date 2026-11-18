import bpy, numpy as np
X0,X1,Y0,Y1=-65,55,250,360
for o in bpy.context.scene.objects:
    if o.type!='MESH' or o.name.startswith('RZ_StudentCenter') : continue
    me=o.data; n=len(me.vertices)
    if n==0: continue
    bb=[o.matrix_world@__import__('mathutils').Vector(c) for c in o.bound_box]
    if min(v.x for v in bb)>X1 or max(v.x for v in bb)<X0 or min(v.y for v in bb)>Y1 or max(v.y for v in bb)<Y0: continue
    if max(v.z for v in bb)>160 and n<50: continue
    co=np.zeros(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
    M=np.array(o.matrix_world); w=co@M[:3,:3].T+M[:3,3]
    m=(w[:,0]>X0)&(w[:,0]<X1)&(w[:,1]>Y0)&(w[:,1]<Y1)
    if m.sum()==0: continue
    print('O',o.name[:60],'|',[c.name[:40] for c in o.users_collection][:1],n,int(m.sum()),round(w[m,2].min(),2),round(w[m,2].max(),2), 'pts' if len(me.polygons)==0 else '')
