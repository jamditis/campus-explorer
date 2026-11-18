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
BX=(-168,-86,-302,-276)
tris_v=[];tris_f=[]
for ob in sc.objects:
    if ob.type!='MESH' or ob.name in skip or ob.name.startswith('WS138b_') or 'tree' in ob.name.lower() or 'shrub' in ob.name.lower() or ob.hide_render: continue
    bb=[ob.matrix_world@Vector(c) for c in ob.bound_box]
    if max(c.x for c in bb)<BX[0] or min(c.x for c in bb)>BX[1] or max(c.y for c in bb)<BX[2] or min(c.y for c in bb)>BX[3]: continue
    if len(ob.data.polygons)>3000000: continue
    ev=ob.evaluated_get(dg); me_=ev.to_mesh(); mw=ob.matrix_world; base=len(tris_v)
    keep={}
    for p in me_.polygons:
        c=mw@p.center
        if BX[0]-2<c.x<BX[1]+2 and BX[2]-2<c.y<BX[3]+2:
            idx=[]
            for i in p.vertices:
                if i not in keep: keep[i]=len(tris_v); tris_v.append(mw@me_.vertices[i].co)
                idx.append(keep[i])
            tris_f.append(idx)
    ev.to_mesh_clear()
print('BVH faces',len(tris_f))
TG=BVHTree.FromPolygons(tris_v,tris_f)
def need(x,y):
    if TL.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))[0] is not None: return False
    g=dz(x,y); h=TG.ray_cast(Vector((x,y,g+6)),Vector((0,0,-1)),12)
    if h[0] is None: return True
    return h[0].z < g-0.35
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
left=0
print('cells still needing fill (sparse check)',left)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
