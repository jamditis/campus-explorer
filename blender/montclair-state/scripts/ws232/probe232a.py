# ws232 probe a: W53b CELS/Calcia NE corner. EVALUATED walks/paving vs evaluated top ground vs USGS 3DEP 1 m, box x 112..152, y 182..252
import bpy,sys,os,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
M='/workspace/nj-scenes/montclair-state/'
P=np.load(M+'scripts/ws230/dep1m_full_x-280_280_y-280_280_rowS.npy')
PM=np.load(M+'scripts/ws230/pad_mask230.npy') if os.path.exists(M+'scripts/ws230/pad_mask230.npy') else None
def p3(x,y):
    gx=x+280-0.5; gy=y+280-0.5; i=int(np.floor(gy)); j=int(np.floor(gx)); fy=gy-i; fx=gx-j
    return float(P[i,j]*(1-fx)*(1-fy)+P[i,j+1]*fx*(1-fy)+P[i+1,j]*(1-fx)*fy+P[i+1,j+1]*fx*fy)
G=['Terrain_LiDAR_DTM_1m','WS60_terrain_edge_apron_LiDAR_to_skirt','QG_north_strip_LiDAR_terrain_patch','QH_east_fan_LiDAR_terrain_patch','QI_east_edge_LiDAR_terrain_patch','QW_DTM_north_edge_ramp_UNVERIFIED','QM_terrain_band_underlay_UNVERIFIED','WU_richardson_reid_LiDAR_patch_UNVERIFIED']
W=['Roads_OSM','Footpaths_OSM','OW3_CELS_walk_road_curb_lip_UNVERIFIED','OX_CELS_walk_road_lip_smoothed_UNVERIFIED','OY_walk_panel_tone_CELS_Calcia_UNVERIFIED','PB2_walk_lawn_fillet_UNVERIFIED','TR_footway_546643369_S_gap_UNVERIFIED','QS_footway_546643369_UNVERIFIED','QS_service_546643370_UNVERIFIED']
with bpy.data.libraries.load(M+os.environ.get('PF','montclair_state.blend'),link=False) as (src,dst):
    dst.objects=[n for n in G+W if n in src.objects]
O=[o for o in dst.objects if o]
for o in O: bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get(); GB=[]; WB={}
for o in O:
    e=o.evaluated_get(dg); mm=e.to_mesh(); Mw=o.matrix_world
    if len(mm.polygons)==0: e.to_mesh_clear(); print('P232A nofaces',o.name); continue
    bv=BVHTree.FromPolygons([Mw@v.co for v in mm.vertices],[p.vertices[:] for p in mm.polygons])
    (WB if o.name in W else dict())[o.name]=bv
    if o.name in G: GB.append((o.name,bv))
    print('P232A loaded',o.name,len(mm.polygons),[m.name for m in o.modifiers],flush=True)
    e.to_mesh_clear()
def hits(bv,x,y):
    out=[]; z=400
    for _ in range(6):
        h=bv.ray_cast(Vector((x,y,z)),Vector((0,0,-1)))
        if h[0] is None: break
        out.append(h[0].z); z=h[0].z-0.01
    return out
rows=[]
for x in np.arange(112,153,2.0):
    for y in np.arange(182,253,2.0):
        d=p3(x,y); g=[(max(hits(b,x,y)),n) for n,b in GB if hits(b,x,y)]
        top=max(g) if g else (None,None)
        pad=None
        if PM is not None:
            try: pad=bool(PM[int(y+280),int(x+280)])
            except Exception: pass
        ws={n:[round(z,2) for z in hits(b,x,y)] for n,b in WB.items() if hits(b,x,y)}
        rows.append((x,y,round(d,2),None if top[0] is None else round(top[0],2),top[1],pad,ws,{n:[round(z,2) for z in hits(b,x,y)] for n,b in GB if hits(b,x,y)}))
import json
json.dump(rows,open(M+'scripts/ws232/probe232a_rows.json','w'))
# summary
dd=[r[3]-r[2] for r in rows if r[3] is not None]
print('P232A top-ground minus 3DEP: n',len(dd),'min',round(min(dd),2),'med',round(float(np.median(dd)),2),'max',round(max(dd),2))
for n in W:
    s=[]
    for r in rows:
        if n in r[6] and r[3] is not None: s.append((r[6][n][0]-r[3], r[6][n][0]-r[2], r[0], r[1]))
    if s: print('P232A',n,'n',len(s),'z-top',round(min(t[0] for t in s),2),round(float(np.median([t[0] for t in s])),2),round(max(t[0] for t in s),2),'z-3dep',round(min(t[1] for t in s),2),round(float(np.median([t[1] for t in s])),2),round(max(t[1] for t in s),2),'worst',sorted(s)[:4],flush=True)
sys.stdout.flush(); os._exit(0)
