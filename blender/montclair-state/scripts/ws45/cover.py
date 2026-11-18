import bpy,numpy as np
from mathutils import Vector
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(src,link=False) as (fr,to):
    names=[n for n in fr.objects if not n.startswith('T_') and not any(k in n.lower() for k in ('grass','tuft','clover','leaf','scatter','shrub','flower','annual','cam'))]
    to.objects=names
sc=bpy.context.scene
for o in to.objects:
    if o and o.type=='MESH' and not o.hide_render: sc.collection.objects.link(o)
print('CV linked',len(sc.objects))
dg=bpy.context.evaluated_depsgraph_get()
Z=np.load('/workspace/nj-scenes/montclair-state/scripts/ws45/Z.npy'); xs=np.arange(-200,140,0.5); ys=np.arange(-130,130,0.5)
gy,gx=np.gradient(Z,0.5); S=np.degrees(np.arctan(np.hypot(gx,gy)))
out=[]
for j,i in zip(*np.where(S>40)):
    x,y=xs[i],ys[j]; h=sc.ray_cast(dg,Vector((x,y,Z[j,i]+60)),Vector((0,0,-1)))
    first=h[4].name if h[0] else None
    if first=='Terrain_LiDAR_DTM_1m' or (h[0] and h[1].z<Z[j,i]-0.02): out.append((x,y,S[j,i],Z[j,i]))
np.save('/workspace/nj-scenes/montclair-state/scripts/ws45/exposed.npy',np.array(out)); print('CV exposed',len(out))
