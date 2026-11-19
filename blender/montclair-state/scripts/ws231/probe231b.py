# ws231 probe b: EVALUATED Footpaths_OSM / Roads_OSM (drape GN on) at W53l and W53k vs evaluated ground + 3DEP; terrain pit map at W53l
import bpy,sys,os,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
M='/workspace/nj-scenes/montclair-state/'
P=np.load(M+'scripts/ws230/dep1m_full_x-280_280_y-280_280_rowS.npy')
def p3(x,y):
    gx=x+280-0.5; gy=y+280-0.5; i=int(np.floor(gy)); j=int(np.floor(gx)); fy=gy-i; fx=gx-j
    return float(P[i,j]*(1-fx)*(1-fy)+P[i,j+1]*fx*(1-fy)+P[i+1,j]*(1-fx)*fy+P[i+1,j+1]*fx*fy)
G=['Terrain_LiDAR_DTM_1m','WS60_terrain_edge_apron_LiDAR_to_skirt','WS230_NE_east_gap_fill_3DEP_UNVERIFIED']
with bpy.data.libraries.load(M+os.environ.get('PF','montclair_state.blend'),link=False) as (src,dst):
    dst.objects=G+['Roads_OSM','Footpaths_OSM']+[n for n in src.objects if n.startswith('WS231')]
O=[o for o in dst.objects if o]
for o in O: bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get(); B=[]; PV={}
for o in O:
    e=o.evaluated_get(dg); mm=e.to_mesh(); W=o.matrix_world
    bv=BVHTree.FromPolygons([W@v.co for v in mm.vertices],[p.vertices[:] for p in mm.polygons])
    if o.name in ('Roads_OSM','Footpaths_OSM'): PV[o.name]=(bv,[W@v.co for v in mm.vertices])
    else: B.append((o.name,bv))
    e.to_mesh_clear()
def gz(x,y):
    zs=[(h.z,n) for h,n in ((b.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0],n) for n,b in B) if h is not None]
    return max(zs) if zs else (None,None)
for nm,(bv,vs) in PV.items():
    for lab,(x0,x1,y0,y1) in (('W53l',(150,175,228,262)),('W53k',(203,238,160,228)),('W53m',(238,252,-44,-14))):
        d=[]
        for w in vs:
            if x0<w.x<x1 and y0<w.y<y1:
                g=gz(w.x,w.y)[0]; d.append((round(w.x,1),round(w.y,1),round(w.z,2),round(w.z-p3(w.x,w.y),2),None if g is None else round(w.z-g,2)))
        if d: print('P231B',nm,lab,len(d),'z-3dep',min(t[3] for t in d),max(t[3] for t in d),'z-ground',min(t[4] for t in d if t[4] is not None),max(t[4] for t in d if t[4] is not None),sorted(d,key=lambda t:t[4] if t[4] is not None else 0)[:8],flush=True)
pit=[]
for x in np.arange(150,176,1.0):
    for y in np.arange(228,252,1.0):
        g,n=gz(x,y)
        if g is not None and g<p3(x,y)-0.3: pit.append((x,y,round(g-p3(x,y),2),n))
print('P231B pit cells',len(pit),pit[:60],flush=True)
# W53k ground strip beside the street, 1 m grid
s=[]
for x in np.arange(203,238,1.0):
    for y in np.arange(160,228,1.0):
        g,n=gz(x,y); h=PV['Roads_OSM'][0].ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]
        if h is not None and g is not None: s.append(h.z-g)
print('P231B W53k road over ground (1 m grid)',len(s),round(min(s),2) if s else None,round(float(np.median(s)),2) if s else None,round(max(s),2) if s else None,flush=True)
sys.stdout.flush(); os._exit(0)
