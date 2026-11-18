import bpy, numpy as np, os
from mathutils import Vector
R='/workspace/nj-scenes/montclair-state/'
DT=np.load(R+'data/dtm_1m.npy'); H=DT.shape[0]/2
def dtm(x,y):
    fx=x+H-0.5; fy=y+H-0.5; j=int(np.floor(fx)); i=int(np.floor(fy)); a=fx-j; b=fy-i
    return float(DT[i,j]*(1-a)*(1-b)+DT[i,j+1]*a*(1-b)+DT[i+1,j]*(1-a)*b+DT[i+1,j+1]*a*b)
X0,X1,Y0,Y1=-238,-212,-238,-198
dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
    if o.type!='MESH' or not o.name.startswith(('Terrain_LiDAR','WS113_terrain_fan','WS110_ground')): continue
    e=o.evaluated_get(dg); me=e.to_mesh(); mw=o.matrix_world; hi=[]
    for f in me.polygons:
        c=mw@f.center
        if X0<c.x<X1 and Y0<c.y<Y1:
            dz=c.z-dtm(c.x,c.y)
            if abs(dz)>0.15: hi.append((round(c.x,1),round(c.y,1),round(dz,2),round(f.area,1)))
    print('F115 EVAL',o.name[:30],len(hi),sorted(hi,key=lambda t:-abs(t[2]))[:15])
    e.to_mesh_clear()
    bh=[]
    for v in o.data.vertices:
        w=mw@v.co
        if X0<w.x<X1 and Y0<w.y<Y1:
            dz=w.z-dtm(w.x,w.y)
            if abs(dz)>0.15: bh.append((v.index,round(w.x,1),round(w.y,1),round(dz,2)))
    print('F115 BASE',o.name[:30],len(bh),bh[:25])
for o in bpy.data.objects:
    if o.type=='MESH' and ('Chapin' in o.name):
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        if min(v.x for v in bb)<X1 and max(v.x for v in bb)>X0 and min(v.y for v in bb)<Y1 and max(v.y for v in bb)>Y0: print('F115 bld',o.name[:50],round(min(v.x for v in bb),1),round(max(v.x for v in bb),1),round(min(v.y for v in bb),1),round(max(v.y for v in bb),1),round(min(v.z for v in bb),2))
