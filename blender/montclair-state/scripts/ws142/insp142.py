import bpy, numpy as np, time
from mathutils import Vector
t=time.time()
X0,X1,Y0,Y1=-94,-70,-222,-196
OB=bpy.data.objects
cells={}
for o in bpy.context.scene.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    me=o.data; mw=np.array(o.matrix_world); npl=len(me.polygons)
    if npl==0: continue
    c=np.empty(npl*3); me.polygons.foreach_get('center',c); c=c.reshape(-1,3)@mw[:3,:3].T+mw[:3,3]
    nr=np.empty(npl*3); me.polygons.foreach_get('normal',nr); nr=nr.reshape(-1,3)
    mi=np.empty(npl,dtype=np.int32); me.polygons.foreach_get('material_index',mi)
    sel=np.nonzero((c[:,0]>X0)&(c[:,0]<X1)&(c[:,1]>Y0)&(c[:,1]<Y1))[0]
    print('OBJ',o.name,round(min(xs),1),round(max(xs),1),round(min(ys),1),round(max(ys),1),round(min(zs),2),round(max(zs),2),len(sel),[m.name if m else None for m in me.materials][:6])
    if (max(zs)-min(zs))>8 and 'Terrain' not in o.name and 'ground' not in o.name.lower(): continue
    mats=[m.name if m else '-' for m in me.materials]
    for i in sel:
        k=(int(np.floor(c[i,0])),int(np.floor(c[i,1])))
        z=c[i,2]
        nm=(o.name[:26],mats[mi[i]][:20] if mats else '-')
        cells.setdefault(k,[]).append((round(z,2),nm))
for y in range(Y1-1,Y0-1,-1):
    for x in range(X0,X1):
        L=sorted(cells.get((x,y),[]),reverse=True)
        seen=[];out=[]
        for z,nm in L:
            if nm in seen: continue
            seen.append(nm); out.append((z,)+nm)
            if len(out)>=3: break
        print('C',x,y,out)
print('DONE',time.time()-t)
