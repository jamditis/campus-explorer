# ws138b: fill the ground hole S of the new lot S curb (pre-existing gap between the WS133b patch S edge y -280 and the Normal Ave verge), 2023 DTM lawn.
import bpy, bmesh, os, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE=os.environ.get('SAVE','0')=='1'
W='/workspace/nj-scenes/montclair-state/scripts/'
ZS=np.load(W+'ws138/dtm138_s.npy').astype(float); X0,Y1,R=-185.0,-240.0,4.0
def dz(x,y):
    fi=(x-X0)*R-0.5; fj=(Y1-y)*R-0.5
    i=int(min(max(math.floor(fi),0),ZS.shape[1]-2)); j=int(min(max(math.floor(fj),0),ZS.shape[0]-2)); tx=min(max(fi-i,0),1); ty=min(max(fj-j,0),1)
    return float(ZS[j,i]*(1-tx)*(1-ty)+ZS[j,i+1]*tx*(1-ty)+ZS[j+1,i]*(1-tx)*ty+ZS[j+1,i+1]*tx*ty)
for o in [o for o in bpy.data.objects if o.name.startswith('WS138b_')]: bpy.data.objects.remove(o)
col=bpy.data.collections['WS138_Russ_S_lot']
lawn=bpy.data.materials['COLE_lawn_post2020_bs']
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
lot=[o for o in bpy.data.objects if o.name.startswith('WS138a_Russ_S_and_BK_lot')][0]
TL=BVHTree.FromPolygons([lot.matrix_world@v.co for v in lot.data.vertices],[p.vertices for p in lot.data.polygons if p.normal.z>0.5])
skip=set(o.name for o in col.objects if 'curb' in o.name)
def need(x,y):
    if TL.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))[0] is not None: return False
    g=dz(x,y); o=Vector((x,y,g+6))
    for _ in range(6):
        h=sc.ray_cast(dg,o,Vector((0,0,-1)),distance=8)
        if not h[0]: return True
        if h[4].name in skip or h[4].type!='MESH' or ('tree' in h[4].name.lower()) or ('shrub' in h[4].name.lower()):
            o=h[1]-Vector((0,0,0.002)); continue
        return h[1].z < g-0.35
    return True
S=0.5; xs=np.arange(-168,-86,S); ys=np.arange(-302,-276,S)
cells=[(x,y) for x in xs for y in ys if need(x+S/2,y+S/2)]
print('fill cells',len(cells))
bm=bmesh.new(); V={}
def v(x,y):
    k=(round(x,3),round(y,3))
    if k not in V: V[k]=bm.verts.new((x,y,dz(x,y)-0.01))
    return V[k]
for x,y in cells: bm.faces.new((v(x,y),v(x+S,y),v(x+S,y+S),v(x,y+S)))
for f in bm.faces:
    f.normal_update()
    if f.normal.z<0: f.normal_flip()
me=bpy.data.meshes.new('WS138b_ground_fill_S_of_lot_curb_DTM2023_lawn_UNVERIFIEDcover'); bm.to_mesh(me); bm.free(); me.materials.append(lawn)
uvl=me.uv_layers.new(name='UVMap')
for lp in me.loops:
    p=me.vertices[lp.vertex_index].co; uvl.data[lp.index].uv=(p.x*0.002+0.5,p.y*0.002+0.5)
o=bpy.data.objects.new(me.name,me); col.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get()
left=sum(1 for x in xs[::4] for y in ys[::4] if need(x+0.1,y+0.1))
print('cells still needing fill (sparse check)',left)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
