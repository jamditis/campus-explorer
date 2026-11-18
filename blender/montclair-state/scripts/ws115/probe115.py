import bpy, numpy as np
from mathutils import Vector
R='/workspace/nj-scenes/montclair-state/'
DT=np.load(R+'data/dtm_1m.npy'); H=DT.shape[0]/2
def dtm(x,y):
    fx=x+H-0.5; fy=y+H-0.5; j=int(np.floor(fx)); i=int(np.floor(fy)); a=fx-j; b=fy-i
    return float(DT[i,j]*(1-a)*(1-b)+DT[i,j+1]*a*(1-b)+DT[i+1,j]*(1-a)*b+DT[i+1,j+1]*a*b)
X0,X1,Y0,Y1=-242,-224,-238,-205
for o in bpy.data.objects:
    if o.type!='MESH': continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(v.x for v in bb)<X0 or min(v.x for v in bb)>X1 or max(v.y for v in bb)<Y0 or min(v.y for v in bb)>Y1: continue
    mw=o.matrix_world; fs=[]
    for f in o.data.polygons:
        c=mw@f.center
        if X0<=c.x<=X1 and Y0<=c.y<=Y1: fs.append((round(c.x,1),round(c.y,1),round(c.z-dtm(c.x,c.y),2),round(f.area,2)))
    if fs: print('P115',o.name[:60],'hid',o.hide_render,'mods',[m.type for m in o.modifiers][:4],'nf',len(fs),'dz rng',min(f[2] for f in fs),max(f[2] for f in fs), fs[:6] if len(fs)<400 else '')
o=next(o for o in bpy.data.objects if o.name.startswith('WS112_CollegeAve_S_E_walk_N_brick'))
V=o.data.vertices; top=np.array([o.matrix_world@V[i].co for i in range(120)]).reshape(24,5,3)
print('P115 brick last row',top[-1].round(3).tolist()); print('P115 brick row -2',top[-2].round(3).tolist())
for y in np.arange(-236,-204,2): print('P115 dtm col', y, [round(dtm(x,y),2) for x in range(-240,-226,2)])
