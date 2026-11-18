"""wx fix3: the grey humps are the QS footway slab's own wall-side verts sitting 20-30 cm above the rest of the slab
(saw-tooth along Stone's west wall). Lower-only: each footway vert within 0.9 m of the Stone footprint -> mean z of the
3 nearest footway TOP verts lying 0.9-2.0 m from the wall (+1 cm), whole vertical stack moved by the same delta."""
import bpy, json, numpy as np, sys, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
R='/workspace/nj-scenes/montclair-state'; O=bpy.data.objects
exec(open(f'{R}/scripts/wx/wx_common.py').read())
def wd(x,y):
    for r in (0.1,0.2,0.3,0.45,0.6,0.75,0.9,1.2,1.5,2.0):
        for t in range(0,360,20):
            if inside(x+r*math.cos(math.radians(t)),y+r*math.sin(math.radians(t))): return r
    return 9
rep={}
for n in ['QS_footway_546643369_UNVERIFIED','QT_soil_edge_546643369_UNVERIFIED']:
    o=O[n]; me=o.data; mw=o.matrix_world; mi=mw.inverted()
    W=[mw@v.co for v in me.vertices]; np.save(f'{R}/data/wx/{n[:10]}_pre_wx.npy',np.array([v.co[:] for v in me.vertices]))
    # top verts: highest at each xy
    key={}
    for i,c in enumerate(W):
        k=(round(c.x,2),round(c.y,2)); key.setdefault(k,[]).append(i)
    tops={k:max(ix,key=lambda i:W[i].z) for k,ix in key.items()}
    d={k:wd(W[i].x,W[i].y) for k,i in tops.items()}
    far=[(k,i) for k,i in tops.items() if 0.9<d[k]<=2.0]
    if not far: print('NOFAR',n); continue
    kd=KDTree(len(far))
    for j,(k,i) in enumerate(far): kd.insert(Vector((W[i].x,W[i].y,0)),j)
    kd.balance(); cnt=0; mx=0
    for k,i in tops.items():
        if d[k]>0.9: continue
        nb=kd.find_n(Vector((W[i].x,W[i].y,0)),3)
        t=np.mean([W[far[j][1]].z for _,j,_ in nb])+0.01
        dz=W[i].z-t
        if dz>0.005:
            for vi in key[k]:
                c=W[vi].copy(); c.z-=dz; me.vertices[vi].co=mi@c
            cnt+=1; mx=max(mx,dz)
    me.update(); rep[n[:10]]=[cnt,round(mx,3)]; print('SMOOTH',n[:10],cnt,round(mx,3),flush=True)
bpy.context.view_layer.update()
json.dump(rep,open(f'{R}/data/wx/fix3_report.json','w'))
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED',len(O),flush=True)
