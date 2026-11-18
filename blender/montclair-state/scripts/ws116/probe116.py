import bpy, numpy as np
from mathutils import Vector
R='/workspace/nj-scenes/montclair-state/'
DT=np.load(R+'data/dtm_1m.npy'); H=DT.shape[0]/2
def dtm(x,y):
    fx=x+H-0.5; fy=y+H-0.5; j=int(np.floor(fx)); i=int(np.floor(fy)); a=fx-j; b=fy-i
    return float(DT[i,j]*(1-a)*(1-b)+DT[i,j+1]*a*(1-b)+DT[i+1,j]*(1-a)*b+DT[i+1,j+1]*a*b)
X0,X1,Y0,Y1=-236,-206,-206,-178
dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(v.x for v in bb)<X0 or min(v.x for v in bb)>X1 or max(v.y for v in bb)<Y0 or min(v.y for v in bb)>Y1: continue
    if o.name.startswith(('T_','Tree')): continue
    e=o.evaluated_get(dg); me=e.to_mesh(); mw=o.matrix_world; fs=[]
    for f in me.polygons:
        c=mw@f.center
        if X0<=c.x<=X1 and Y0<=c.y<=Y1 and f.normal.z>0.5: fs.append((round(c.x,1),round(c.y,1),round(c.z-dtm(c.x,c.y),2),round(f.area,2)))
    e.to_mesh_clear()
    if fs:
        dz=[f[2] for f in fs]; ar=sum(f[3] for f in fs)
        print('P116',o.name[:70],'nf',len(fs),'area %.0f'%ar,'dz min %.2f med %.2f max %.2f'%(min(dz),float(np.median(dz)),max(dz)),'mods',[m.type for m in o.modifiers][:3])
for y in range(-206,-176,2): print('P116 dtm y',y,[round(dtm(x,y),2) for x in range(-236,-204,2)])
