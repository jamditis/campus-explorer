# ws256b (UNIFY W63h): same as ws255d (W63g) one step south: the 2020 ortho's Feliciano building shadow continues on the grass
# plot EAST of the ws253/ws254 walk south of the OSM path (x -189.7..wall+12, y 176..190.8; dark patch in the ws256 junction test).
# Shadow-dark texels -> ws247_lawn = 1 (1-ring 0.5) on the terrain and the WS250 patch; material attribute only.
# ws255d (UNIFY W63g): the 2020 ortho bakes Feliciano's building shadow onto the lawn along its E wall north of the OSM walk
# (x wall..wall+10, y 191..212; seen as a dark band in the ws255 oblique). Terrain verts there whose ortho texel is shadow-dark
# get ws247_lawn = 1 (1-ring 0.5), which mixes them toward the ws247 constant lawn colour in Ground_ortho_grass (geometry unchanged).
# Stays south of University Hall's site (y >= 221). Lit lawn texels in the same box are reported for comparison.
import bpy, numpy as np
TAG='F256B'
def inner(y): return -194.69+0.0615*(y-172.0)
img=next(n.image for n in bpy.data.materials['Ground_ortho_grass'].node_tree.nodes if n.type=='TEX_IMAGE' and n.image and 'ortho' in n.image.name.lower())
w,h=img.size; px=np.empty(w*h*4,np.float32); img.pixels.foreach_get(px); px=px.reshape(h,w,4)
def col(u,v): return px[min(h-1,max(0,int(v*h))),min(w-1,max(0,int(u*w))),:3]
import mathutils
# ws255d2: the W63 lawn here is the WS250 LiDAR patch joined into the terrain by GN (render-hidden source object), so the
# attribute must be on the patch too (first ws255d test, terrain only: no visible change).
for ON in ('Terrain_LiDAR_DTM_1m','WS250_W63_lawn_LiDAR2023_ground_patch_1m'):
    T=bpy.data.objects[ON]; me=T.data; M=T.matrix_world; uvl=me.uv_layers['ortho'].data
    lv=np.empty(len(me.loops),np.int32); me.loops.foreach_get('vertex_index',lv)
    uv=np.empty(len(me.loops)*2,np.float32); uvl.foreach_get('uv',uv); uv=uv.reshape(-1,2)
    co=np.empty(len(me.vertices)*3,np.float32); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
    W=np.array([M@__import__('mathutils').Vector(c) for c in co[:0]]) if False else None
    import mathutils
    box=[]
    for li in range(len(lv)):
        p=M@mathutils.Vector(co[lv[li]])
        if 176.0<=p.y<=190.8 and -189.7<=p.x<=inner(p.y)+12.0: box.append((lv[li],p,col(*uv[li])))
    lum={}
    for v,p,c in box: lum.setdefault(v,[]).append(float(c.sum()))
    L={v:np.mean(s) for v,s in lum.items()}
    vals=np.array(list(L.values())); print(TAG,ON,'box verts',len(L),'lum p10 %.3f p50 %.3f p90 %.3f'%tuple(np.percentile(vals,[10,50,90])),flush=True)
    thr=1.02  # lit lawn texels in the box are >= 1.05 (display RGB sum), the shadow band 0.57-0.98
    dark={v for v,l in L.items() if l<thr}
    print(TAG,ON,'thr %.3f dark %d'%(thr,len(dark)),flush=True)
    for y0 in range(176,191,3):
        row=sorted([( (M@mathutils.Vector(co[v])).x-inner((M@mathutils.Vector(co[v])).y), L[v]) for v in L if y0<=(M@mathutils.Vector(co[v])).y<y0+1])
        print(TAG,ON,'y%d'%y0,' '.join('%.1f:%.2f%s'%(d,l,'*' if l<thr else '') for d,l in row),flush=True)
    ring=set()
    for p in me.polygons:
        vs=p.vertices[:]
        if any(v in dark for v in vs): ring.update(v for v in vs if v not in dark)
    at=me.attributes.get('ws247_lawn') or me.attributes.new('ws247_lawn','FLOAT','POINT')
    f=np.zeros(len(me.vertices),np.float32); at.data.foreach_get('value',f)
    for v in ring: f[v]=max(f[v],0.5)
    for v in dark: f[v]=1.0
    at.data.foreach_set('value',f); me.update(); print(TAG,ON,'set ones',len(dark),'ring',len(ring),flush=True)
